from flask import Blueprint

from app.routes.checkin import checkin_bp

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    A simple route for the homepage.
    This can serve as a basic entry point for the app.
    """
    return "Hello, Flask"