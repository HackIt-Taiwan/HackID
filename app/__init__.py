# app/__init__.py
from datetime import timedelta
import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO
from flask_mailman import Mail
from flask_limiter import Limiter

from dotenv import load_dotenv
from mongoengine import connect
from openai import AsyncAzureOpenAI, AsyncOpenAI
from redis import Redis

from app.utils.request_utils import get_real_ip

socketio = SocketIO()
cors = CORS()
openai = None
app = Flask(__name__)
mail = Mail()
limiter = Limiter(
    key_func=get_real_ip,
    default_limits=[
        f"{os.getenv('LIMITER_DAILY_LIMIT', '6000')} per day",
        f"{os.getenv('LIMITER_HOURLY_LIMIT', '1000')} per hour"
    ]
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="請求過於頻繁，請稍後再試"), 429

def create_app():
    global openai, app
    load_dotenv()

    # App configuration
    app.config['DEBUG'] = os.getenv('DEBUG') == 'True'

    if os.getenv('REDIS_URI') is None or os.getenv('REDIS_URI') == '':
        app.config['SESSION_TYPE'] = 'filesystem'
    else:
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = Redis.from_url(os.getenv('REDIS_URI'))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=int(os.getenv('SESSION_TIMEOUT', 604800)))
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'sess:'

    # Mail configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'false').lower() in ['true', 'on', '1']
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # OPENAI configuration and initialization
    if os.getenv('USE_AZURE_OPENAI') == 'True':
        openai = AsyncAzureOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION')
        )
    else:
        openai = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Here to load blueprint
    from app.routes.index import index_bp
    from app.routes.image_viewr import image_bp
    from app.routes.api.flash_messages import flash_message_bp

    # Here to initialize the app
    connect(host=os.getenv('MONGO_URI'))
    Session(app)
    socketio.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # Here to register blueprint
    app.register_blueprint(index_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(flash_message_bp, url_prefix='/api/v1')

    # Here to register sockets

    return app
