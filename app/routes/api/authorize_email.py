# app/routes/api/authorize.py
import base64
import datetime
import io

from PIL import Image
from flask import Blueprint, request, jsonify, session, redirect, url_for

from app import limiter
from app.models.staff import Staff, EmergencyContact
from app.utils.helpers.authorize import get_jwt_token, set_jwt_cookie, find_staff_by_uuid, is_valid_api_key, \
    verify_jwt_token
from app.utils.redis_client import redis_client
from app.utils.helpers.authorize import send_verification_code_email, find_staff_by_email

authorize_api_email_bp = Blueprint('authorize_api_email', __name__)


@authorize_api_email_bp.route('/register', methods=['POST'])
@limiter.limit("3 per minute; 20 per hour; 60 per day")
def api_register():
    """API endpoint for registration."""
    try:
        data = request.get_json()
        if not data or 'uuid' not in data or 'email' not in data:
            return jsonify({'error': '無效的請求'}), 400

        user_uuid = data['uuid']
        email = data['email']

        # Search for staff object with the given uuid
        is_valid, staff = find_staff_by_uuid(user_uuid, email)
        if not is_valid:
            return jsonify({'error': "查無此人或驗證失敗"}), 400

        # Send verification code to email
        send_verification_code_email(staff.email, staff)

        return jsonify({'message': 'Verification code sent'}), 200
    except Exception as e:
        return jsonify({'error': "查無此人或驗證失敗"}), 400


@authorize_api_email_bp.route('/login', methods=['POST'])
@limiter.limit("3 per minute; 20 per hour; 60 per day")
def api_login():
    """API endpoint for login."""
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': '無效的請求'}), 400

    email = data['email']
    is_valid, staff = find_staff_by_email(email)
    if not is_valid:
        return jsonify({'error': '查無此人或驗證失敗'}), 400

    if not staff.is_signup:
        return jsonify({'error': '請先透過識別碼註冊'}), 400

    # Send verification code to email
    send_verification_code_email(staff.email, staff)

    return jsonify({'message': 'Verification code sent'}), 200


@authorize_api_email_bp.route('/verify_code', methods=['POST'])
@limiter.limit("5 per minute; 80 per hour; 300 per day")
def api_verify_code():
    """API endpoint to verify the code and log the user in."""
    data = request.get_json()
    if not data or 'email' not in data or 'code' not in data:
        return jsonify({'error': '無效的請求'}), 400

    email = data['email']
    code = data['code']
    is_valid, staff = find_staff_by_email(email)
    if not is_valid:
        return jsonify({'error': '查無此人或驗證失敗'}), 400

    # Retrieve code from Redis
    redis_key = f'verification_code:{staff.uuid}'
    stored_code = redis_client.get(redis_key)
    if not stored_code or stored_code.decode('utf-8') != code:
        return jsonify({'error': '驗證碼錯誤或已過期'}), 400

    # Code is valid, delete it from Redis
    redis_client.delete(redis_key)

    # Log the user in by setting session and JWT cookie
    session['user_id'] = str(staff.uuid)

    # Prepare JWT token
    payload = {
        'user_id': str(staff.uuid),
        'email': staff.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    token = get_jwt_token(payload)

    response = jsonify({'message': 'Login successful'})

    # Set JWT cookie with domain '.hackit.tw'
    set_jwt_cookie(response, token)

    return response


@authorize_api_email_bp.route('/verify_jwt', methods=['POST'])
@limiter.limit("6 per minute")
def api_verify_jwt():
    """API endpoint for SSO clients to verify the JWT token and get user data."""
    api_key = request.headers.get('X-API-Key')
    if not api_key or not is_valid_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    token = data['token']
    payload = verify_jwt_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # Fetch user data
    user_id = payload.get('user_id')
    email = payload.get('email')

    staff = Staff.find_user_by_uuid(user_id)
    if not staff or staff.email != email:
        return jsonify({'error': 'User not found or invalid'}), 404

    # Return user data
    user_data = {
        'user_id': user_id,
        'email': email,
        'name': staff.name,
    }

    return jsonify({'message': 'Token is valid', 'user': user_data}), 200


@authorize_api_email_bp.route('/register/save', methods=['POST'])
@limiter.limit("12 per minute")
def save_registration_data():
    token = request.cookies.get('jwt')

    if not token:
        return jsonify({'error': '未經授權的請求'}), 401

    payload = verify_jwt_token(token)
    if not payload:
        return jsonify({'error': '未經授權的請求'}), 401

    user_id = payload.get('user_id')
    staff = Staff.find_user_by_uuid(user_id)
    if not staff:
        return jsonify({'error': '用戶不存在'}), 404

    # Stage 1:
    phone_number = request.form.get('phone_number', staff.phone_number)
    if phone_number:
        phone_number = phone_number.strip()
        if phone_number.startswith('8869'):
            phone_number = '0' + phone_number[3:]
        if len(phone_number) != 10 or not phone_number.isdigit():
            return jsonify({'error': '手機號碼無效，必須為10位數字'}), 400

        staff.phone_number = phone_number

    staff.city = request.form.get('city', staff.city)
    staff.school = request.form.get('school', staff.school)

    # Stage 2:
    emergency_contact_data = request.form.get('emergency_contact')
    if emergency_contact_data:
        import json
        contact_data = json.loads(emergency_contact_data)
        staff.emergency_contact = EmergencyContact(
            name=contact_data['name'],
            relationship=contact_data['relationship'],
            phone_number=contact_data['phone_number']
        )

    # Stage 3:
    staff.nickname = request.form.get('nickname', staff.nickname)
    staff.line_id = request.form.get('line_id', staff.line_id)
    staff.ig_id = request.form.get('ig_id', staff.ig_id)
    staff.introduction = request.form.get('introduction', staff.introduction)

    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file:

            try:
                avatar = Image.open(avatar_file)

                if avatar.mode == 'RGBA':
                    avatar = avatar.convert('RGB')

                max_size = 3 * 1024 * 1024
                img_byte_arr = io.BytesIO()
                avatar.save(img_byte_arr, format='JPEG', quality=85)
                img_byte_arr = img_byte_arr.getvalue()

                if len(img_byte_arr) > max_size:
                    avatar.thumbnail((avatar.width // 2, avatar.height // 2))
                    img_byte_arr = io.BytesIO()
                    avatar.save(img_byte_arr, format='JPEG', quality=85)
                    img_byte_arr = img_byte_arr.getvalue()

                staff.avatar_base64 = 'data:image/jpeg;base64,' + base64.b64encode(img_byte_arr).decode('utf-8')

            except Exception as e:
                return jsonify({'error': f'圖片處理失敗: {str(e)}'}), 400

    staff.save()
    return jsonify({'message': '資料已儲存'}), 200


@authorize_api_email_bp.route('/register/complete', methods=['POST'])
@limiter.limit("5 per minute")
def complete_registration():
    token = request.cookies.get('jwt')

    if not token:
        return jsonify({'error': '未經授權的請求'}), 401

    payload = verify_jwt_token(token)
    if not payload:
        return jsonify({'error': '未經授權的請求'}), 401

    user_id = payload.get('user_id')
    staff = Staff.find_user_by_uuid(user_id)
    if not staff:
        return jsonify({'error': '用戶不存在'}), 404

    # Check if all required fields are filled
    required_fields = ['name', 'email', 'phone_number', 'city', 'school', 'nickname', 'line_id', "avatar_base64"]
    for field in required_fields:
        if not getattr(staff, field, None):
            return jsonify({'error': f'請填寫完整的 {field} 資料'}), 400

    if not staff.emergency_contact:
        return jsonify({'error': '請填寫緊急聯絡人'}), 400

    if not staff.avatar_base64:
        return jsonify({'error': '請上傳頭像'}), 400

    staff.is_signup = True
    staff.save()
    return jsonify({'message': '註冊完成'}), 200
