# app/routes/api/authorize.py
import datetime
from flask import Blueprint, request, jsonify, session, redirect, url_for

from app import limiter
from app.models.staff import Staff
from app.utils.helpers.authorize import get_jwt_token, set_jwt_cookie, find_staff_by_uuid, is_valid_api_key, \
    verify_jwt_token
from app.utils.redis_client import redis_client
from app.utils.helpers.authorize import send_verification_code_email, find_staff_by_email

authorize_api_email_bp = Blueprint('authorize_api_email', __name__)


@authorize_api_email_bp.route('/register', methods=['POST'])
@limiter.limit("3 per minute; 20 per hour; 60 per day")
def api_register():
    """API endpoint for registration."""
    data = request.get_json()
    if not data or 'uuid' not in data or 'email' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    user_uuid = data['uuid']
    email = data['email']

    # Search for staff object with the given uuid
    is_valid, staff = find_staff_by_uuid(user_uuid, email)
    if not is_valid:
        return jsonify({'error': 'Validation failed'}), 400

    # Send verification code to email
    send_verification_code_email(staff.email, staff)

    return jsonify({'message': 'Verification code sent'}), 200


@authorize_api_email_bp.route('/login', methods=['POST'])
@limiter.limit("3 per minute; 20 per hour; 60 per day")
def api_login():
    """API endpoint for login."""
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    email = data['email']
    is_valid, staff = find_staff_by_email(email)
    if not is_valid:
        return jsonify({'error': 'Validation failed'}), 400

    if not staff.is_signup:
        return redirect(url_for('authorize_api_email.api_register'), code=307)

    # Send verification code to email
    send_verification_code_email(staff.email, staff)

    return jsonify({'message': 'Verification code sent'}), 200


@authorize_api_email_bp.route('/verify_code', methods=['POST'])
@limiter.limit("5 per minute; 80 per hour; 300 per day")
def api_verify_code():
    """API endpoint to verify the code and log the user in."""
    data = request.get_json()
    if not data or 'email' not in data or 'code' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    email = data['email']
    code = data['code']
    is_valid, staff = find_staff_by_email(email)
    if not is_valid:
        return jsonify({'error': 'Validation failed'}), 400

    # Retrieve code from Redis
    redis_key = f'verification_code:{staff.uuid}'
    stored_code = redis_client.get(redis_key)
    if not stored_code or stored_code.decode('utf-8') != code:
        return jsonify({'error': 'Invalid or expired code'}), 400

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
