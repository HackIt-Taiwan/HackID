from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app(config_class):
    """
    Initialize the Flask application with the given configuration.
    Register the necessary Blueprints for routing.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)

    from app.routes import main_bp, checkin_bp, category_bp, sign_upload_bp, RFID_check_in_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(sign_upload_bp)
    app.register_blueprint(RFID_check_in_bp)

    return app