from flask import Flask
from flask_jwt_extended import JWTManager

from app.auth.route import auth_bp
from app.books.route import book_bp
from app.errors import register_error_handlers
from app.loan.route import loan_bp
from app.members.route import member_bp
from app.quiz.route import quiz_bp
from app.utils.logger import setup_logging
from config import Config
from db.database import init_pool, release_conn

jwt = JWTManager()


def create_app(config_override=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if config_override:
        app.config.update(config_override)

    init_pool(app)
    app.teardown_appcontext(release_conn)

    jwt.init_app(app)

    register_error_handlers(app)
    setup_logging(app)

    app.register_blueprint(book_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(quiz_bp)

    return app