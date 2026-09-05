import re
from functools import wraps

from flask import Blueprint, jsonify, request
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

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ============================================================
# ROLE CONFIGURATION
# ============================================================

# Numeric hierarchical roles.
#
# Higher number = higher permission level.
#
# 5  = guest
# 15 = member
# 20 = admin

ROLE_GUEST = 5
ROLE_MEMBER = 15
ROLE_LIBRARIAN = 20

_VALID_ROLES = (
    ROLE_GUEST,
    ROLE_MEMBER,
    ROLE_LIBRARIAN,
)


# ============================================================
# VALIDATION
# ============================================================

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


# ============================================================
# ROLE DECORATOR
# ============================================================


def role_required(required_role):
    """
    Require the authenticated user to have at least required_role.

    Example:

        @role_required(ROLE_MEMBER)

    A user with:

        role = 5   -> 403
        role = 15  -> allowed
        role = 20  -> allowed
    """

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
                                id,
                                role,
                                is_active
                            FROM users
                            WHERE id = %s
                            """,
                            (user_id,),
                        )

                        user = cur.fetchone()

                # JWT is valid, but the user no longer exists.
                if not user:
                    return jsonify(
                        {
                            "error": "user not found",
                            "code": 401,
                        }
                    ), 401

                # User exists but has been disabled.
                if not user["is_active"]:
                    return jsonify(
                        {
                            "error": "account is inactive",
                            "code": 401,
                        }
                    ), 401

                user_role = user["role"]

                # Protect against unexpected role values.
                if user_role not in _VALID_ROLES:
                    return jsonify(
                        {
                            "error": "invalid user role",
                            "code": 403,
                        }
                    ), 403

                # Hierarchical authorization:
                #
                # user role  < required role
                #        => insufficient permission
                #
                if user_role < required_role:
                    return jsonify(
                        {
                            "error": "insufficient permissions",
                            "code": 403,
                        }
                    ), 403

                # Authorization succeeded.
                return func(*args, **kwargs)

            except Exception:
                return jsonify(
                    {
                        "error": "internal server error",
                        "code": 500,
                    }
                ), 500

        return wrapper

    return decorator


# ============================================================
# SIGNUP
# ============================================================


@auth_bp.route("/signup", methods=["POST"])
def signup():

    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    display_name = (data.get("display_name") or "").strip()
    mobile_number = (data.get("mobile_number") or "").strip()

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not email or not password:
        return jsonify(
            {
                "error": "email and password are required",
                "code": 400,
            }
        ), 400

    if not EMAIL_RE.match(email):
        return jsonify(
            {
                "error": "invalid email format",
                "code": 400,
            }
        ), 400

    if len(password) < 8:
        return jsonify(
            {
                "error": "password must be at least 8 characters",
                "code": 400,
            }
        ), 400

    if mobile_number and not PHONE_RE.match(mobile_number):
        return jsonify(
            {
                "error": "invalid mobile number",
                "code": 400,
            }
        ), 400

    try:
        with get_db() as conn:  # noqa: SIM117
            with conn.cursor() as cur:
                # ------------------------------------------------
                # Check whether email already exists
                # ------------------------------------------------

                cur.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE email = %s
                    """,
                    (email,),
                )

                existing_user = cur.fetchone()

                if existing_user:
                    return jsonify(
                        {
                            "error": "email already exists",
                            "code": 409,
                        }
                    ), 409

                # ------------------------------------------------
                # Hash password
                # ------------------------------------------------

                password_hash = generate_password_hash(password)

                # ------------------------------------------------
                # Create user
                #
                # New users start as MEMBER.
                # ------------------------------------------------

                cur.execute(
                    """
                    INSERT INTO users (
                        email,
                        password,
                        display_name,
                        mobile_number,
                        role,
                        is_active
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        TRUE
                    )
                    RETURNING
                        id,
                        email,
                        display_name,
                        mobile_number,
                        role,
                        is_active
                    """,
                    (
                        email,
                        password_hash,
                        display_name or None,
                        mobile_number or None,
                        ROLE_MEMBER,
                    ),
                )

                user = cur.fetchone()

        return jsonify(
            {
                "id": str(user["id"]),
                "email": user["email"],
                "display_name": user["display_name"],
                "mobile_number": user["mobile_number"],
                "role": user["role"],
                "is_active": user["is_active"],
            }
        ), 201

    except Exception:
        return jsonify(
            {
                "error": "internal server error",
                "code": 500,
            }
        ), 500


# ============================================================
# LOGIN
# ============================================================


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    identifier = (data.get("identifier") or data.get("email") or "").strip().lower()

    password = data.get("password") or ""

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not identifier or not password:
        return jsonify(
            {
                "error": "identifier and password are required",
                "code": 400,
            }
        ), 400

    # Determine whether the user is logging in with
    # email or phone number.
    if EMAIL_RE.match(identifier):
        lookup_col = "email"

    elif PHONE_RE.match(identifier):
        lookup_col = "mobile_number"

    else:
        return jsonify(
            {
                "error": "identifier must be a valid email or phone number",
                "code": 400,
            }
        ), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # lookup_col is NOT user input.
                # It can only be "email" or "mobile_number"
                # because of the validation above.
                cur.execute(
                    f"""
                    SELECT
                        id,
                        email,
                        password,
                        display_name,
                        mobile_number,
                        role,
                        is_active
                    FROM users
                    WHERE {lookup_col} = %s
                    """,
                    (identifier,),
                )

                user = cur.fetchone()

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        if not user:
            return jsonify(
                {
                    "error": "invalid credentials",
                    "code": 401,
                }
            ), 401

        if not user["is_active"]:
            return jsonify(
                {
                    "error": "account is inactive",
                    "code": 401,
                }
            ), 401

        if not user["password"]:
            return jsonify(
                {
                    "error": "invalid credentials",
                    "code": 401,
                }
            ), 401

        if not check_password_hash(
            user["password"],
            password,
        ):
            return jsonify(
                {
                    "error": "invalid credentials",
                    "code": 401,
                }
            ), 401

        # ----------------------------------------------------
        # Create JWT tokens
        # ----------------------------------------------------

        user_id = str(user["id"])

        access_token = create_access_token(identity=user_id)

        refresh_token = create_refresh_token(identity=user_id)

        return jsonify(
            {
                "id": user_id,
                "email": user["email"],
                "display_name": user["display_name"],
                "mobile_number": user["mobile_number"],
                "role": user["role"],
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ), 200

    except Exception:
        return jsonify(
            {
                "error": "internal server error",
                "code": 500,
            }
        ), 500


# ============================================================
# REFRESH ACCESS TOKEN
# ============================================================


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
                        id,
                        role,
                        is_active
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,),
                )

                user = cur.fetchone()

        # ----------------------------------------------------
        # User must still exist
        # ----------------------------------------------------

        if not user:
            return jsonify(
                {
                    "error": "user not found",
                    "code": 401,
                }
            ), 401

        # ----------------------------------------------------
        # User must still be active
        # ----------------------------------------------------

        if not user["is_active"]:
            return jsonify(
                {
                    "error": "account is inactive",
                    "code": 401,
                }
            ), 401

        # ----------------------------------------------------
        # Create new access token
        # ----------------------------------------------------

        access_token = create_access_token(identity=str(user["id"]))

        return jsonify(
            {
                "access_token": access_token,
            }
        ), 200

    except Exception:
        return jsonify(
            {
                "error": "internal server error",
                "code": 500,
            }
        ), 500


# ============================================================
# CURRENT USER
# ============================================================


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
                        id,
                        email,
                        display_name,
                        mobile_number,
                        role,
                        is_active
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,),
                )

                user = cur.fetchone()

        # ----------------------------------------------------
        # JWT is valid but user doesn't exist
        # ----------------------------------------------------

        if not user:
            return jsonify(
                {
                    "error": "user not found",
                    "code": 404,
                }
            ), 404

        # ----------------------------------------------------
        # User exists but is disabled
        # ----------------------------------------------------

        if not user["is_active"]:
            return jsonify(
                {
                    "error": "account is inactive",
                    "code": 401,
                }
            ), 401

        return jsonify(
            {
                "id": str(user["id"]),
                "email": user["email"],
                "display_name": user["display_name"],
                "mobile_number": user["mobile_number"],
                "role": user["role"],
                "is_active": user["is_active"],
            }
        ), 200

    except Exception:
        return jsonify(
            {
                "error": "internal server error",
                "code": 500,
            }
        ), 500


# ============================================================
# EXAMPLE PROTECTED ENDPOINTS
# ============================================================
#
# These demonstrate how the RBAC decorator is actually used.
#
# IMPORTANT:
# Do NOT add @jwt_required() to these endpoints.
#
# role_required() already performs JWT authentication.
#


@auth_bp.route("/guest-area", methods=["GET"])
@role_required(ROLE_GUEST)
def guest_area():

    return jsonify(
        {
            "message": "You can access the guest area.",
        }
    ), 200


@auth_bp.route("/member-area", methods=["GET"])
@role_required(ROLE_MEMBER)
def member_area():

    return jsonify(
        {
            "message": "You can access the member area.",
        }
    ), 200


@auth_bp.route("/admin-area", methods=["GET"])
@role_required(ROLE_LIBRARIAN)
def admin_area():

    return jsonify(
        {
            "message": "You can access the admin area.",
        }
    ), 200
