import re
from functools import wraps

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from db.database import get_db


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


# Roles stored as strings in the users table.
ROLE_GUEST = "guest"
ROLE_MEMBER = "member"
ROLE_LIBRARIAN = "librarian"
ROLE_ADMIN = "admin"

# Numeric ordering so we can compare "is at least".
_ROLE_ORDER = {
    ROLE_GUEST: 5,
    ROLE_MEMBER: 15,
    ROLE_LIBRARIAN: 20,
    ROLE_ADMIN: 20,
}

_VALID_ROLES = set(_ROLE_ORDER.keys())


EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

PHONE_RE = re.compile(
    r"^\+?[0-9]{10,15}$"
)


def role_required(required_role):
    

    if required_role not in _VALID_ROLES:
        raise ValueError("Invalid required role")

    required_level = _ROLE_ORDER[required_role]

    def decorator(func):

        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()

            try:
                with get_db() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT
                                user_id,
                                role,
                                is_active
                            FROM users
                            WHERE user_id = %s
                            """,
                            (user_id,),
                        )

                        user = cur.fetchone()

                if not user:
                    return jsonify({
                        "error": "user not found",
                        "code": 401,
                    }), 401

                if not user["is_active"]:
                    return jsonify({
                        "error": "account is inactive",
                        "code": 401,
                    }), 401

                user_role = user["role"]

                if user_role not in _VALID_ROLES:
                    return jsonify({
                        "error": "invalid user role",
                        "code": 403,
                    }), 403

                if _ROLE_ORDER[user_role] < required_level:
                    return jsonify({
                        "error": "insufficient permissions",
                        "code": 403,
                    }), 403

                return func(*args, **kwargs)

            except Exception:
                return jsonify({
                    "error": "internal server error",
                    "code": 500,
                }), 500

        return wrapper

    return decorator


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    display_name = (data.get("display_name") or "").strip()
    mobile_number = (
        data.get("mobile_number") or ""
    ).strip()

    if not email or not password:
        return jsonify({
            "error": "email and password are required",
            "code": 400,
        }), 400

    if not EMAIL_RE.fullmatch(email):
        return jsonify({
            "error": "invalid email format",
            "code": 400,
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "password must be at least 8 characters",
            "code": 400,
        }), 400

    if mobile_number and not PHONE_RE.fullmatch(
        mobile_number
    ):
        return jsonify({
            "error": "invalid mobile number",
            "code": 400,
        }), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE email = %s
                    """,
                    (email,),
                )

                if cur.fetchone():
                    return jsonify({
                        "error": "email already exists",
                        "code": 409,
                    }), 409

                password_hash = generate_password_hash(
                    password
                )

                cur.execute(
                    """
                    INSERT INTO users (
                        email,
                        password_hash,
                        role,
                        is_active
                    )
                    VALUES (
                        %s, %s, %s, TRUE
                    )
                    RETURNING
                        user_id,
                        email,
                        role,
                        is_active
                    """,
                    (
                        email,
                        password_hash,
                        ROLE_MEMBER,
                    ),
                )

                user = cur.fetchone()

            conn.commit()

        return jsonify({
            "id": str(user["user_id"]),
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"],
        }), 201

    except Exception:
        return jsonify({
            "error": "internal server error",
            "code": 500,
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    
    current_app.logger.warning(
    "LOGIN DEBUG: data=%r content_type=%r raw=%r",
    data,
    request.content_type,
    request.get_data(as_text=True),
)

    identifier = (
        data.get("identifier")
        or data.get("email")
        or ""
    ).strip().lower()

    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({
            "error": "identifier and password are required",
            "code": 400,
        }), 400

    # users table only has email, not phone.
    if not EMAIL_RE.fullmatch(identifier):
        return jsonify({
            "error": "identifier must be a valid email",
            "code": 400,
        }), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        user_id,
                        email,
                        password_hash,
                        role,
                        is_active
                    FROM users
                    WHERE email = %s
                    """,
                    (identifier,),
                )

                user = cur.fetchone()

        if not user:
            return jsonify({
                "error": "invalid credentials",
                "code": 401,
            }), 401

        if not user["is_active"]:
            return jsonify({
                "error": "account is inactive",
                "code": 401,
            }), 401

        if not user["password_hash"]:
            return jsonify({
                "error": "invalid credentials",
                "code": 401,
            }), 401

        if not check_password_hash(
            user["password_hash"],
            password,
        ):
            return jsonify({
                "error": "invalid credentials",
                "code": 401,
            }), 401

        user_id = str(user["user_id"])

        access_token = create_access_token(
            identity=user_id
        )

        refresh_token = create_refresh_token(
            identity=user_id
        )

        return jsonify({
            "id": user_id,
            "email": user["email"],
            "role": user["role"],
            "access_token": access_token,
            "refresh_token": refresh_token,
        }), 200

    except Exception:
        return jsonify({
            "error": "internal server error",
            "code": 500,
        }), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        user_id,
                        is_active
                    FROM users
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )

                user = cur.fetchone()

        if not user:
            return jsonify({
                "error": "user not found",
                "code": 401,
            }), 401

        if not user["is_active"]:
            return jsonify({
                "error": "account is inactive",
                "code": 401,
            }), 401

        access_token = create_access_token(
            identity=str(user["user_id"])
        )

        return jsonify({
            "access_token": access_token,
        }), 200

    except Exception:
        return jsonify({
            "error": "internal server error",
            "code": 500,
        }), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        user_id,
                        email,
                        role,
                        is_active
                    FROM users
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )

                user = cur.fetchone()

        if not user:
            return jsonify({
                "error": "user not found",
                "code": 404,
            }), 404

        if not user["is_active"]:
            return jsonify({
                "error": "account is inactive",
                "code": 401,
            }), 401

        return jsonify({
            "id": str(user["user_id"]),
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"],
        }), 200

    except Exception:
        return jsonify({
            "error": "internal server error",
            "code": 500,
        }), 500


@auth_bp.route("/guest-area", methods=["GET"])
@role_required(ROLE_GUEST)
def guest_area():
    return jsonify({
        "message": "You can access the guest area."
    }), 200


@auth_bp.route("/member-area", methods=["GET"])
@role_required(ROLE_MEMBER)
def member_area():
    return jsonify({
        "message": "You can access the member area."
    }), 200


@auth_bp.route("/admin-area", methods=["GET"])
@role_required(ROLE_LIBRARIAN)
def admin_area():
    return jsonify({
        "message": "You can access the librarian area."
    }), 200