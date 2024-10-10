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

    from app.routes import main_bp, checkin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(checkin_bp)

    return app