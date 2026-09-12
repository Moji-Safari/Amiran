import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()



BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    TESTING = False

    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Database pool
    DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", 2))
    DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", 10))

    # JWT
    #SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=50)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Uploads
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
    )

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads",
        "book_covers",
    )

    ALLOWED_IMAGE_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp",
    }

    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    @classmethod
    def validate(cls):
        cls._validate_required()
        cls._validate_integers()
        cls._validate_ranges()

    @classmethod
    def _validate_required(cls):
        required = {
            "SECRET_KEY": cls.SECRET_KEY,
            "JWT_SECRET_KEY": cls.JWT_SECRET_KEY,
            "DB_HOST": cls.DB_HOST,
            "DB_PORT": cls.DB_PORT,
            "DB_NAME": cls.DB_NAME,
            "DB_USER": cls.DB_USER,
            "DB_PASSWORD": cls.DB_PASSWORD,
        }

        missing = [
            name
            for name, value in required.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing required configuration: "
                + ", ".join(missing)
            )

    @classmethod
    def _validate_integers(cls):
        integer_fields = [
            "DB_PORT",
            "DB_POOL_MIN",
            "DB_POOL_MAX",
            "MAX_CONTENT_LENGTH",
        ]

        for field in integer_fields:
            value = getattr(cls, field)

            try:
                setattr(cls, field, int(value))
            except (TypeError, ValueError):
                raise RuntimeError(
                    f"{field} must be an integer, got {value!r}"
                )

    @classmethod
    def _validate_ranges(cls):
        if not 1 <= cls.DB_PORT <= 65535:
            raise RuntimeError(
                f"DB_PORT must be between 1 and 65535, "
                f"got {cls.DB_PORT}"
            )

        if cls.DB_POOL_MIN < 1:
            raise RuntimeError(
                "DB_POOL_MIN must be at least 1"
            )

        if cls.DB_POOL_MAX < cls.DB_POOL_MIN:
            raise RuntimeError(
                "DB_POOL_MAX must be greater than or equal "
                "to DB_POOL_MIN"
            )

        if cls.MAX_CONTENT_LENGTH <= 0:
            raise RuntimeError(
                "MAX_CONTENT_LENGTH must be greater than 0"
            )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "")


class TestingConfig(Config):
    TESTING = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}