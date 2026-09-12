from flask import Blueprint, current_app, request
from flask_jwt_extended import (
    get_jwt_identity,
)

from app.auth.route import (
    ROLE_LIBRARIAN,
    ROLE_MEMBER,
    role_required,
)
from db.database import get_db
from app.utils.validator import (
    validate_borrow_request,
    validate_positive_id,
)


loan_bp = Blueprint(
    "loan",
    __name__,
    url_prefix="/loan",
)


STATUS_PENDING = 1
STATUS_APPROVED = 2
STATUS_BORROWED = 4


def get_member_by_user_id(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    PK_memb_id AS memb_id,
                    user_id,
                    FK_branch_id AS branch_id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    membership_type,
                    join_date
                FROM members
                WHERE user_id = %s
                """,
                (user_id,),
            )

            member = cur.fetchone()

    if member is None:
        return None

    return dict(member)


@loan_bp.route("/demand", methods=["POST"])
@role_required(ROLE_MEMBER)
def create_request():
    user_id = get_jwt_identity()

    member = get_member_by_user_id(user_id)

    if member is None:
        return {
            "error": "Member not found"
        }, 404

    data = request.get_json(silent=True) or {}

    error = validate_borrow_request(data)

    if error:
        return {"error": error}, 400

    book_id = data["book_id"]
    member_id = member["memb_id"]
    branch_id = member["branch_id"]

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                # Make sure the book exists.
                cur.execute(
                    """
                    SELECT book_id
                    FROM books
                    WHERE book_id = %s
                    """,
                    (book_id,),
                )

                if cur.fetchone() is None:
                    return {
                        "error": "Book not found"
                    }, 404

                # Check active loans.
                cur.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM loan
                    WHERE FK_memb_id = %s
                      AND loanstatus_id IN (%s, %s)
                    """,
                    (
                        member_id,
                        STATUS_PENDING,
                        STATUS_APPROVED,
                    ),
                )

                active_count = cur.fetchone()["count"]

                if active_count >= 3:
                    return {
                        "error": (
                            "Member already has "
                            "3 active loans"
                        )
                    }, 400

                # Check whether book is unavailable.
                cur.execute(
                    """
                    SELECT 1
                    FROM loan
                    WHERE FK_book_id = %s
                      AND loanstatus_id IN (%s, %s)
                    LIMIT 1
                    """,
                    (
                        book_id,
                        STATUS_PENDING,
                        STATUS_APPROVED,
                    ),
                )

                if cur.fetchone() is not None:
                    return {
                        "error": "Book is currently unavailable"
                    }, 400

                cur.execute(
                    """
                    INSERT INTO loan (
                        FK_branch_id,
                        FK_book_id,
                        loanstatus_id,
                        FK_memb_id
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING PK_loan_id AS loan_id
                    """,
                    (
                        branch_id,
                        book_id,
                        STATUS_PENDING,
                        member_id,
                    ),
                )

                loan_id = cur.fetchone()["loan_id"]

            conn.commit()

        return {
            "message": "Loan request created",
            "loan_id": loan_id,
        }, 201

    except Exception:
        current_app.logger.exception(
            "Failed to create loan request"
        )

        return {
            "error": "Failed to create loan request"
        }, 500


@loan_bp.route(
    "/approved/<int:state>",
    methods=["GET", "POST"],
)
@role_required(ROLE_LIBRARIAN)
def pending_operations(state):
    if state <= 0:
        return {
            "error": "state must be positive"
        }, 400

    if request.method == "GET":
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            PK_loan_id AS loan_id,
                            loanstatus_id
                        FROM loan
                        WHERE loanstatus_id = %s
                        ORDER BY PK_loan_id
                        """,
                        (state,),
                    )

                    pending_list = cur.fetchall()

            return {
                "loans": pending_list
            }, 200

        except Exception:
            current_app.logger.exception(
                "Failed to retrieve loan operations"
            )

            return {
                "error": "Failed to retrieve loans"
            }, 500

    data = request.get_json(silent=True) or {}

    loan_id = data.get("loan_id")

    error = validate_positive_id(
        loan_id,
        "loan_id",
    )

    if error:
        return {"error": error}, 400

    due_date = data.get("due_date")
    return_date = data.get("return_date")

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE loan
                    SET
                        loanstatus_id = %s,
                        due_date = %s,
                        return_date = %s
                    WHERE PK_loan_id = %s
                      AND loanstatus_id = %s
                    RETURNING PK_loan_id AS loan_id
                    """,
                    (
                        STATUS_APPROVED,
                        due_date,
                        return_date,
                        loan_id,
                        state,
                    ),
                )

                loan = cur.fetchone()

                if loan is None:
                    return {
                        "error": (
                            "Loan not found or "
                            "cannot be approved"
                        )
                    }, 400

            conn.commit()

        return {
            "message": "Loan approved",
            "loan_id": loan["loan_id"],
        }, 200

    except Exception:
        current_app.logger.exception(
            "Failed to approve loan"
        )

        return {
            "error": "Failed to approve loan"
        }, 500


@loan_bp.route("/borrow", methods=["POST"])
@role_required(ROLE_MEMBER)
def borrow_book():
    """
    Change the member's reserved loan to borrowed.
    """

    user_id = get_jwt_identity()

    member = get_member_by_user_id(user_id)

    if member is None:
        return {
            "error": "Member not found"
        }, 404

    data = request.get_json(silent=True) or {}

    loan_id = data.get("loan_id")

    error = validate_positive_id(
        loan_id,
        "loan_id",
    )

    if error:
        return {"error": error}, 400

    member_id = member["memb_id"]

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE loan
                    SET loanstatus_id = %s
                    WHERE PK_loan_id = %s
                      AND FK_memb_id = %s
                      AND loanstatus_id = %s
                    RETURNING PK_loan_id AS loan_id
                    """,
                    (
                        STATUS_APPROVED,
                        loan_id,
                        member_id,
                        STATUS_PENDING,
                    ),
                )

                loan = cur.fetchone()

                if loan is None:
                    return {
                        "error": (
                            "Loan not found or "
                            "cannot be borrowed"
                        )
                    }, 400

            conn.commit()

        return {
            "message": "Book borrowed successfully",
            "loan_id": loan["loan_id"],
        }, 200

    except Exception:
        current_app.logger.exception(
            "Failed to borrow book"
        )

        return {
            "error": "Failed to borrow book"
        }, 500


@loan_bp.route(
    "/cancel/<int:loan_id>",
    methods=["DELETE"],
)
@role_required(ROLE_MEMBER)
def cancel_loan(loan_id):
    user_id = get_jwt_identity()

    member = get_member_by_user_id(user_id)

    if member is None:
        return {
            "error": "Member not found"
        }, 404

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE loan
                    SET loanstatus_id = %s
                    WHERE PK_loan_id = %s
                      AND FK_memb_id = %s
                      AND loanstatus_id IN (%s, %s)
                    RETURNING PK_loan_id AS loan_id
                    """,
                    (
                        STATUS_BORROWED,
                        loan_id,
                        member["memb_id"],
                        STATUS_PENDING,
                        STATUS_APPROVED,
                    ),
                )

                loan = cur.fetchone()

                if loan is None:
                    return {
                        "error": (
                            "Loan not found or "
                            "cannot be cancelled"
                        )
                    }, 400

            conn.commit()

        return {
            "message": "Loan cancelled",
            "loan_id": loan["loan_id"],
        }, 200

    except Exception:
        current_app.logger.exception(
            "Failed to cancel loan"
        )

        return {
            "error": "Failed to cancel loan"
        }, 500