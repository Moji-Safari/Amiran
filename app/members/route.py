from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.auth.route import ROLE_LIBRARIAN, ROLE_MEMBER, role_required
from app.db.database import get_db
from app.auth.decorators import role_required
from app.auth.constants import ROLE_LIBRARIAN


member_bp = Blueprint("members", __name__, url_prefix="/members")


# ============================================================
# Helpers / Validation
# ============================================================

def escape_like(value: str) -> str:
    """
    Escape PostgreSQL ILIKE wildcard characters.

    %  -> literal %
    _  -> literal _
    \\ -> literal backslash
    """
    return (
        value
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def validate_member_data(data, partial=False):
    """
    Validate member input.

    If partial=True, only fields supplied by the client are validated.
    """

    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    allowed_fields = {
        "branch_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "membership_type",
    }

    unknown_fields = set(data.keys()) - allowed_fields

    if unknown_fields:
        field = next(iter(unknown_fields))
        return f"Unknown field: {field}"

    if not partial:
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "membership_type",
        ]

        for field in required_fields:
            if field not in data:
                return f"{field} is required"

    # branch_id
    if "branch_id" in data and data["branch_id"] is not None:
        if not isinstance(data["branch_id"], int):
            return "branch_id must be an integer"

        if data["branch_id"] <= 0:
            return "branch_id must be greater than 0"

    # first_name
    if "first_name" in data:
        if not isinstance(data["first_name"], str):
            return "first_name must be a string"

        if not data["first_name"].strip():
            return "first_name cannot be empty"

        if len(data["first_name"]) > 100:
            return "first_name cannot exceed 100 characters"

    # last_name
    if "last_name" in data:
        if not isinstance(data["last_name"], str):
            return "last_name must be a string"

        if not data["last_name"].strip():
            return "last_name cannot be empty"

        if len(data["last_name"]) > 100:
            return "last_name cannot exceed 100 characters"

    # email
    if "email" in data:
        if not isinstance(data["email"], str):
            return "email must be a string"

        if not data["email"].strip():
            return "email cannot be empty"

        if len(data["email"]) > 255:
            return "email cannot exceed 255 characters"

    # phone
    if "phone" in data and data["phone"] is not None:
        if not isinstance(data["phone"], str):
            return "phone must be a string"

        if len(data["phone"]) > 50:
            return "phone cannot exceed 50 characters"

    # membership_type
    if "membership_type" in data:
        if not isinstance(data["membership_type"], str):
            return "membership_type must be a string"

        if not data["membership_type"].strip():
            return "membership_type cannot be empty"

        if len(data["membership_type"]) > 50:
            return "membership_type cannot exceed 50 characters"

    return None


# ============================================================
# CREATE MEMBER
# POST /members
# ============================================================

@member_bp.route("/create", methods=["POST"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def create_member():

    data = request.get_json()

    error = validate_member_data(data)

    if error:
        return {"error": error}, 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                # Check that branch exists if branch_id was supplied
                branch_id = data.get("branch_id")

                if branch_id is not None:
                    cur.execute(
                        """
                        SELECT branch_id
                        FROM branches
                        WHERE branch_id = %s
                        """,
                        (branch_id,),
                    )

                    if cur.fetchone() is None:
                        return {"error": "Branch not found"}, 404

                # Check duplicate email
                cur.execute(
                    """
                    SELECT memb_id
                    FROM members
                    WHERE email = %s
                    """,
                    (data["email"],),
                )

                if cur.fetchone() is not None:
                    return {"error": "Email already exists"}, 409

                cur.execute(
                    """
                    INSERT INTO members (
                        branch_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        membership_type
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING
                        memb_id,
                        branch_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        membership_type,
                        join_date
                    """,
                    (
                        branch_id,
                        data["first_name"].strip(),
                        data["last_name"].strip(),
                        data["email"].strip(),
                        data.get("phone"),
                        data["membership_type"].strip(),
                    ),
                )

                member = cur.fetchone()

            conn.commit()

        return {
            "message": "Member created successfully",
            "member": member,
        }, 201

    except Exception:
        return {"error": "Failed to create member"}, 500


# ============================================================
# GET ONE MEMBER
# GET /members/<memb_id>
# ============================================================

@member_bp.route("/find/<int:memb_id>", methods=["GET"])
@jwt_required()
def get_member(memb_id):

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        memb_id,
                        branch_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        membership_type,
                        join_date
                    FROM members
                    WHERE memb_id = %s
                    """,
                    (memb_id,),
                )

                member = cur.fetchone()

        if member is None:
            return {"error": "Member not found"}, 404

        return {"member": member}, 200

    except Exception:
        return {"error": "Failed to retrieve member"}, 500


# ============================================================
# GET MEMBERS
# GET /members
#
# Examples:
#
# /members
# /members?page=1
# /members?page=2&limit=10
# /members?search=ali&page=1&limit=10
# ============================================================

@member_bp.route("/lst", methods=["GET"])
@jwt_required()
def get_members():

    search = request.args.get("search", "").strip()

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    # Validate pagination
    if page < 1:
        return {"error": "page must be greater than or equal to 1"}, 400

    if limit < 1:
        return {"error": "limit must be greater than or equal to 1"}, 400

    # Prevent huge requests
    if limit > 100:
        return {"error": "limit cannot exceed 100"}, 400

    offset = (page - 1) * limit

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                # ------------------------------------------------
                # Escape user search input
                # ------------------------------------------------

                escaped_search = escape_like(search)
                search_pattern = f"%{escaped_search}%"

                # ------------------------------------------------
                # Count total matching members
                # ------------------------------------------------

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM members
                    WHERE first_name ILIKE %s ESCAPE '\\'
                       OR last_name ILIKE %s ESCAPE '\\'
                       OR email ILIKE %s ESCAPE '\\'
                    """,
                    (
                        search_pattern,
                        search_pattern,
                        search_pattern,
                    ),
                )

                total = cur.fetchone()[0]

                # ------------------------------------------------
                # Get current page
                # ------------------------------------------------

                cur.execute(
                    """
                    SELECT
                        memb_id,
                        branch_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        membership_type,
                        join_date
                    FROM members
                    WHERE first_name ILIKE %s ESCAPE '\\'
                       OR last_name ILIKE %s ESCAPE '\\'
                       OR email ILIKE %s ESCAPE '\\'
                    ORDER BY memb_id
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        search_pattern,
                        search_pattern,
                        search_pattern,
                        limit,
                        offset,
                    ),
                )

                members = cur.fetchall()

        return {
            "members": members,
            "page": page,
            "limit": limit,
            "total": total,
        }, 200

    except Exception:
        return {"error": "Failed to retrieve members"}, 500


# ============================================================
# UPDATE MEMBER
# PATCH /members/<memb_id>
# ============================================================

@member_bp.route("/update/<int:memb_id>", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def update_member(memb_id):

    data = request.get_json()

    error = validate_member_data(data, partial=True)

    if error:
        return {"error": error}, 400

    if not data:
        return {"error": "At least one field is required"}, 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                # Check member exists
                cur.execute(
                    """
                    SELECT memb_id
                    FROM members
                    WHERE memb_id = %s
                    """,
                    (memb_id,),
                )

                if cur.fetchone() is None:
                    return {"error": "Member not found"}, 404

                # Check branch if supplied
                if "branch_id" in data and data["branch_id"] is not None:

                    cur.execute(
                        """
                        SELECT branch_id
                        FROM branches
                        WHERE branch_id = %s
                        """,
                        (data["branch_id"],),
                    )

                    if cur.fetchone() is None:
                        return {"error": "Branch not found"}, 404

                # Check email uniqueness if email is being changed
                if "email" in data:

                    cur.execute(
                        """
                        SELECT memb_id
                        FROM members
                        WHERE email = %s
                          AND memb_id <> %s
                        """,
                        (
                            data["email"].strip(),
                            memb_id,
                        ),
                    )

                    if cur.fetchone() is not None:
                        return {"error": "Email already exists"}, 409

                # ------------------------------------------------
                # Build UPDATE dynamically
                # ------------------------------------------------

                allowed_fields = [
                    "branch_id",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "membership_type",
                ]

                updates = []
                values = []

                for field in allowed_fields:

                    if field not in data:
                        continue

                    updates.append(f"{field} = %s")

                    value = data[field]

                    if isinstance(value, str):
                        value = value.strip()

                    values.append(value)

                if not updates:
                    return {"error": "No valid fields provided"}, 400

                values.append(memb_id)

                query = f"""
                    UPDATE members
                    SET {", ".join(updates)}
                    WHERE memb_id = %s
                    RETURNING
                        memb_id,
                        branch_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        membership_type,
                        join_date
                """

                cur.execute(query, values)

                member = cur.fetchone()

            conn.commit()

        return {
            "message": "Member updated successfully",
            "member": member,
        }, 200

    except Exception:
        return {"error": "Failed to update member"}, 500


# ============================================================
# DELETE MEMBER
# DELETE /members/<memb_id>
# ============================================================

@member_bp.route("/delete/<int:memb_id>", methods=["DELETE"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def delete_member(memb_id):

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    DELETE FROM members
                    WHERE memb_id = %s
                    RETURNING memb_id
                    """,
                    (memb_id,),
                )

                deleted_member = cur.fetchone()

            conn.commit()

        if deleted_member is None:
            return {"error": "Member not found"}, 404

        return {
            "message": "Member deleted successfully",
            "memb_id": deleted_member["memb_id"],
        }, 200

    except Exception:
        return {"error": "Failed to delete member"}, 500