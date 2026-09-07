from flask import Flask
from app.errors import register_error_handlers

from config import MAX_CONTENT_LENGTH, UPLOAD_FOLDER, Config
from flask_jwt_extended import JWTManager
from app.utils.logger import setup_logging


jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    jwt.init_app(app)
    register_error_handlers(app)
    setup_logging(app)

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    return app
