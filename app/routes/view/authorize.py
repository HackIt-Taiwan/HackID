# app/routes/view/authorize.py
from flask import Blueprint, render_template, request, session, url_for, redirect, make_response, jsonify

from app import limiter
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
