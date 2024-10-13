# app/routes/view/authorize.py
from flask import Blueprint, render_template, request, session, url_for, redirect, make_response, jsonify

from app import limiter
from app.models.staff import Staff
from app.utils.helpers.authorize import verify_jwt_token

authorize_bp = Blueprint('authorize', __name__)

@authorize_bp.route('/login')
def login():
    """Render the login page or redirect if already authenticated."""
    token = request.cookies.get('jwt')

    if token:
        payload = verify_jwt_token(token)
        if payload:
            # JWT is valid, proceed to redirect
            redirect_url = session.pop('redirect_url', None) or request.args.get('redirect') or url_for('index.home')
            return redirect(redirect_url)
        else:
            # JWT is invalid or expired, delete the cookie
            response = make_response(
                render_template('login.html', uuid=request.args.get('uuid', ''), email=request.args.get('email', '')))
            response.delete_cookie('jwt', domain='.hackit.tw')  # Ensure the domain matches
            return response

    # No JWT, proceed to render login page
    if request.args.get('redirect'):
        redirect_url = request.args.get('redirect')
        session['redirect_url'] = redirect_url

    return render_template('login.html', uuid=request.args.get('uuid', ''), email=request.args.get('email', ''))


@authorize_bp.route('/logout')
def logout():
    """Logout the user by deleting the session and JWT cookie, then redirect appropriately."""
    if 'user_id' in session:
        session.pop('user_id')

    redirect_url = request.args.get('redirect')
    response = redirect(url_for('authorize.login')) if not redirect_url else redirect

    response.delete_cookie(
        'jwt',
        httponly=True,
        secure=True,
        samesite='Lax',
        domain='.hackit.tw'
    )

    return response


@authorize_bp.route('/register')
def register():
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

    staff_data = {
        'name': staff.name,
        'email': staff.email,
        'phone_number': staff.phone_number,
        'city': staff.city,
        'school': staff.school,
        'emergency_contact': {
            'name': staff.emergency_contact.name if staff.emergency_contact else '',
            'relationship': staff.emergency_contact.relationship if staff.emergency_contact else '',
            'phone_number': staff.emergency_contact.phone_number if staff.emergency_contact else ''
        },
        'nickname': staff.nickname,
        'line_id': staff.line_id,
        'ig_id': staff.ig_id,
        'introduction': staff.introduction,
        'avatar_base64': staff.avatar_base64
    }

    return render_template('register.html', staff_data=staff_data)
