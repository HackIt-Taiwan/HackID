# app/routes/api/lark.py
from flask import Blueprint, request, jsonify
from app import limiter
from app.models.staff import Staff, LarkInfo
from app.utils.helpers.authorize import verify_jwt_token
from app.utils.helpers.lark import create_lark_user, get_department_id_by_group

lark_api_bp = Blueprint('lark_api', __name__)


@lark_api_bp.route('/create-lark', methods=['POST'])
@limiter.limit("4 per minute")
def create_email():
    token = request.cookies.get('jwt')

    if not token:
        return jsonify({'error': '未受授權的請求'}), 401

    payload = verify_jwt_token(token)
    if not payload:
        return jsonify({'error': '未受授權的請求'}), 401

    user_id = payload.get('user_id')
    staff = Staff.find_user_by_uuid(user_id)
    if not staff:
        return jsonify({'error': '內部錯誤'}), 500

    if staff.lark_info:
        return jsonify({'error': '您已有飛書帳號'}), 400

    data = request.get_json()
    desired_email = data.get('desired_email')

    if not desired_email:
        return jsonify({'error': '請提供您想要的企業郵箱地址'}), 400

    # Validate desired_email
    import re
    if not re.match(r'^[a-zA-Z0-9._-]+$', desired_email):
        return jsonify({'error': '企業郵箱地址只能包含字母、數字、點和連字符'}), 400

    # Retrieve Feishu department ID by current group
    success, department_id, error_message = get_department_id_by_group(staff.current_group)
    if not success:
        return jsonify({'error': error_message}), 400

    # department_id to list and append 0 to list
    department_id = ['0', department_id]

    # Build payload to send to Feishu (Lark)
    lark_payload = {
        "name": staff.name,
        "nickname": staff.nickname or staff.name,
        "mobile": "+886" + staff.phone_number[1:],  # Assuming phone_number starts with 0
        "mobile_visible": True,
        "department_ids": department_id,  # Use the found department ID
        "employee_type": 1,
        "email": staff.email,
        "enterprise_email": f"{desired_email}@staff.hackit.tw"
    }

    # Send request to Feishu (Lark) API to create the account
    success, lark_user_id, error_message = create_lark_user(lark_payload)

    if not success:
        return jsonify({'error': error_message}), 400

    # Save LarkInfo in the Staff model
    staff.lark_info = LarkInfo(
        user_id=lark_user_id,
        enterprise_email=lark_payload['enterprise_email']
    )
    staff.save()

    return jsonify({'message': '飛書帳號創建成功'}), 201
