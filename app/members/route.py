from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required

from app.auth.route import (
    ROLE_LIBRARIAN,
    role_required,
)
from db.database import get_db
from app.utils.validator import validate_member_data


member_bp = Blueprint(
    "members",
    __name__,
    url_prefix="/members",
)


def escape_like(value):
    return (
        value
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


@member_bp.route("/create", methods=["POST"])
@role_required(ROLE_LIBRARIAN)
def create_member():
    data = request.get_json(silent=True) or {}

    error = validate_member_data(data)

    if error:
        return {"error": error}, 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
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
                        return {
                            "error": "Branch not found"
                        }, 404

                email = data["email"].strip().lower()

                cur.execute(
                    """
                    SELECT PK_memb_id
                    FROM members
                    WHERE email = %s
                    """,
                    (email,),
                )

                if cur.fetchone() is not None:
                    return {
                        "error": "Email already exists"
                    }, 409

                cur.execute(
                    """
                    INSERT INTO members (
                        FK_branch_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        membership_type
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                    RETURNING
                        PK_memb_id AS memb_id,
                        FK_branch_id AS branch_id,
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
                        email,
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
        current_app.logger.exception(
            "Failed to create member"
        )

        return {
            "error": "Failed to create member"
        }, 500


@member_bp.route("/find/<int:memb_id>", methods=["GET"])
@jwt_required()
def get_member(memb_id):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        PK_memb_id AS memb_id,
                        FK_branch_id AS branch_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        membership_type,
                        join_date
                    FROM members
                    WHERE PK_memb_id = %s
                    """,
                    (memb_id,),
                )

                member = cur.fetchone()

        if member is None:
            return {
                "error": "Member not found"
            }, 404

        return {
            "member": member
        }, 200

    except Exception:
        current_app.logger.exception(
            "Failed to retrieve member"
        )

        return {
            "error": "Failed to retrieve member"
        }, 500


@member_bp.route("/lst", methods=["GET"])
@jwt_required()
def get_members():
    search = request.args.get(
        "search",
        "",
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    limit = request.args.get(
        "limit",
        10,
        type=int,
    )

    if page < 1:
        return {
            "error": "page must be greater than or equal to 1"
        }, 400

    if limit < 1:
        return {
            "error": "limit must be greater than or equal to 1"
        }, 400

    if limit > 100:
        return {
            "error": "limit cannot exceed 100"
        }, 400

    offset = (page - 1) * limit

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                escaped_search = escape_like(search)
                pattern = f"%{escaped_search}%"

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM members
                    WHERE first_name ILIKE %s ESCAPE '\\'
                       OR last_name ILIKE %s ESCAPE '\\'
                       OR email ILIKE %s ESCAPE '\\'
                    """,
                    (
                        pattern,
                        pattern,
                        pattern,
                    ),
                )

                total = cur.fetchone()["count"]

                cur.execute(
                    """
                    SELECT
                        PK_memb_id AS memb_id,
                        FK_branch_id AS branch_id,
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
                    ORDER BY PK_memb_id
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        pattern,
                        pattern,
                        pattern,
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
        current_app.logger.exception(
            "Failed to retrieve members"
        )

        return {
            "error": "Failed to retrieve members"
        }, 500


@member_bp.route(
    "/update/<int:memb_id>",
    methods=["PATCH"],
)
@role_required(ROLE_LIBRARIAN)
def update_member(memb_id):
    data = request.get_json(silent=True) or {}

    if not data:
        return {
            "error": "At least one field is required"
        }, 400

    error = validate_member_data(
        data,
        partial=True,
    )

    if error:
        return {"error": error}, 400

    # API field -> DB column
    field_map = {
        "branch_id": "FK_branch_id",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email",
        "phone": "phone",
        "membership_type": "membership_type",
    }

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT PK_memb_id
                    FROM members
                    WHERE PK_memb_id = %s
                    """,
                    (memb_id,),
                )

                if cur.fetchone() is None:
                    return {
                        "error": "Member not found"
                    }, 404

                if (
                    "branch_id" in data
                    and data["branch_id"] is not None
                ):
                    cur.execute(
                        """
                        SELECT branch_id
                        FROM branches
                        WHERE branch_id = %s
                        """,
                        (data["branch_id"],),
                    )

                    if cur.fetchone() is None:
                        return {
                            "error": "Branch not found"
                        }, 404

                if "email" in data:
                    email = data["email"].strip().lower()

                    cur.execute(
                        """
                        SELECT PK_memb_id
                        FROM members
                        WHERE email = %s
                          AND PK_memb_id <> %s
                        """,
                        (email, memb_id),
                    )

                    if cur.fetchone() is not None:
                        return {
                            "error": "Email already exists"
                        }, 409

                    data["email"] = email

                updates = []
                values = []

                for field, column in field_map.items():
                    if field not in data:
                        continue

                    updates.append(f"{column} = %s")

                    value = data[field]

                    if isinstance(value, str):
                        value = value.strip()

                    values.append(value)

                if not updates:
                    return {
                        "error": "No valid fields provided"
                    }, 400

                values.append(memb_id)

                query = f"""
                    UPDATE members
                    SET {", ".join(updates)}
                    WHERE PK_memb_id = %s
                    RETURNING
                        PK_memb_id AS memb_id,
                        FK_branch_id AS branch_id,
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
        current_app.logger.exception(
            "Failed to update member"
        )

        return {
            "error": "Failed to update member"
        }, 500


@member_bp.route(
    "/delete/<int:memb_id>",
    methods=["DELETE"],
)
@role_required(ROLE_LIBRARIAN)
def delete_member(memb_id):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM members
                    WHERE PK_memb_id = %s
                    RETURNING PK_memb_id AS memb_id
                    """,
                    (memb_id,),
                )

                deleted_member = cur.fetchone()

            conn.commit()

        if deleted_member is None:
            return {
                "error": "Member not found"
            }, 404

        return {
            "message": "Member deleted successfully",
            "memb_id": deleted_member["memb_id"],
        }, 200

    except Exception:
        current_app.logger.exception(
            "Failed to delete member"
        )

        return {
            "error": "Failed to delete member"
        }, 500