# app/routes/view/lark.py
from flask import Blueprint, render_template, request, redirect, url_for
from app.models.staff import Staff
from app.utils.helpers.authorize import verify_jwt_token

lark_bp = Blueprint('lark', __name__)


@lark_bp.route('/create-lark')
def create_lark():
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

    # If lark_info already exists, redirect to dashboard
    if staff.lark_info:
        return redirect(url_for('index.home'))

    return render_template('create_lark.html', staff=staff)
