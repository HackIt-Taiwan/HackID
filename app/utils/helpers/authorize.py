# app/utils/helpers/authorize.py
import hashlib
import os
import secrets
import time

from authlib.jose import jwt
from flask import request, redirect

from app.models.staff import Staff
from app.utils.mail_sender import send_email
from app.utils.redis_client import redis_client


def is_valid_api_key(api_key):
    """Validate the API key."""
    valid_api_keys = os.getenv('VALID_API_KEYS', '').split(',')
    return api_key in valid_api_keys


def generate_verification_code(length=8):
    """Generate a secure random numeric verification code."""
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def get_jwt_token(payload):
    """Generate a JWT token with the given payload."""
    header = {'alg': 'HS256', 'typ': 'JWT'}
    secret = os.getenv('JWT_SECRET_KEY')
    if not secret:
        raise ValueError("JWT_SECRET_KEY environment variable is not set")
    token = jwt.encode(header, payload, secret)
    return token.decode('utf-8')


def verify_jwt_token(token):
    """Verify the JWT token and return the payload if valid."""
    secret = os.getenv('JWT_SECRET_KEY')
    if not secret:
        raise ValueError("JWT_SECRET_KEY environment variable is not set")

    try:
        payload = jwt.decode(token.encode('utf-8'), secret)
        payload.validate()  # This will check the 'exp' and other claims
        return payload
    except Exception as e:
        print(f"JWT verification failed: {e}")
        return None


def set_jwt_cookie(response, token):
    """Set JWT cookie in the response with proper settings."""
    response.set_cookie(
        'jwt',
        token,
        httponly=True,
        secure=True,
        samesite='Lax',
        domain='.hackit.tw'
    )

def send_verification_code_email(email, staff):
    """Send the verification code to the given email address."""
    redis_key = f'verification_code:{staff.uuid}'
    if redis_client.exists(redis_key):
        verification_code = redis_client.get(redis_key).decode('utf-8')
    else:
        verification_code = generate_verification_code()
        redis_client.setex(redis_key, 600, verification_code)

    send_email(
        subject='Hackit / 登入驗證碼',
        recipient=email,
        template='emails/verification_code.html',
        name=staff.name,
        code=verification_code
    )

def find_staff_by_email(email):
    staff = Staff.find_user_by_email(email)
    if not staff:
        return False, None

    # Decrypt and verify the email
    if staff.email != email:
        return False, None

    return True, staff

def find_staff_by_uuid(uuid, email):
    staff = Staff.find_user_by_uuid(uuid)
    if not staff:
        return False, None

    # Decrypt and verify the email
    if staff.email != email:
        return False, None

    return True, staff
