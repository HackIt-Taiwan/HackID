# app/routes/view/index.py
from flask import Blueprint, render_template, request, redirect, url_for

from app.models.staff import Staff
from app.utils.helpers.authorize import verify_jwt_token

index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def home():
    token = request.cookies.get('jwt')

    if not token:
        return redirect(url_for('authorize.login'))

    payload = verify_jwt_token(token)
    if not payload:
        return redirect(url_for('authorize.login'))

    user_id = payload.get('user_id')
    staff = Staff.find_user_by_uuid(user_id)
    if not staff:
        return redirect(url_for('authorize.login'))

    if not staff.is_signup:
        return redirect(url_for('authorize.register'))

    if not staff.lark_info:
        return redirect(url_for('lark.create_lark'))

    return render_template('coming_soon.html')
