from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.auth.route import ROLE_LIBRARIAN, ROLE_MEMBER, role_required
from app.utils.validator import validate_borrow_request
from db.database import get_db

loan_bp = Blueprint("loan", __name__, url_prefix="/loan")

#member information
def get_member_by_user_id(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    memb_id,
                    user_id,
                    branch_id,
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
@jwt_required()
@role_required(ROLE_MEMBER)
def create_request():

    user = get_jwt_identity()
    member = get_member_by_user_id(user)
    if member is None:
        return {"error": "Member not found"}, 404

    member_id = member["memb_id"]
    user_branch = member["branch_id"]




    book_id = request.args.get("book_id", type=int)

    if book_id is None:
        return {"error": "book_id is required"}, 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                # 1. Check member's active loans
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM loan
                    WHERE memb_id = %s
                      AND loanstatus_id IN (1, 2,4)
                    """,
                    (member_id,),
                )

                active_loan_count = cur.fetchone()[0]

                if active_loan_count >= 3:
                    return {
                        "error": "Member already has 3 active loans"
                    }, 400

                # 2. Check whether the book is available
                cur.execute(
                    """
                    SELECT 1
                    FROM loan
                    WHERE book_id = %s
                      AND loanstatus_id IN (1, 2,4)
                    LIMIT 1
                    """,
                    (book_id,),
                )

                book_is_unavailable = cur.fetchone() is not None

                if book_is_unavailable:
                    return {
                        "error": "Book is currently unavailable"
                    }, 400

                # 3. Create loan request
                cur.execute(
                    """
                    INSERT INTO loan (
                        branch_id,
                        book_id,
                        loanstatus_id,
                        memb_id
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING loan_id
                    """,
                    (
                        user_branch,
                        book_id,
                        1,
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
        return {
            "error": "Failed to create loan request"
        }, 500
#for cancel operation we can use DELETE method and <int:x>



@loan_bp.route("/approved/<int:state>", methods=["GET", "POST"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def pending_operations():

    if request.method == "GET":
        with get_db() as conn:  # noqa: SIM117
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT loan_id, loanstatus_id
                    FROM loan
                    WHERE loanstatus_id = %s
                    """,
                    (state,),
                )

                pending_list = cur.fetchall()

        return {"loans": pending_list}, 200

    if request.method == "POST":
        data = request.get_json()

        due_date = data.get("due_date")
        return_date = data.get("return_date")
        loan_id = data.get("loan_id")

        if not loan_id:
            return {"error": "loan_id is required"}, 400

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE loan
                    SET loanstatus_id = %s,
                        due_date = %s,
                        return_date = %s
                    WHERE loan_id = %s
                    """,
                    (2, due_date, return_date, loan_id),
                )

        return {
            "message": "Loan approved",
            "loan_id": loan_id,
        }, 200

@loan_bp.route("/borrow", methods=["POST"])
@jwt_required()
@role_required(ROLE_MEMBER)
def borrow_book():

    user_id = get_jwt_identity()

    member = get_member_by_user_id(user_id)

    if member is None:
        return {"error": "Member not found"}, 404

    data = request.get_json(silent=True)

    error = validate_borrow_request(data)

    if error:
        return {"error": error}, 400

    member_id = member["memb_id"]
    

    data = request.get_json()

    loan_id = data.get("loan_id")

    if loan_id is None:
        return {"error": "loan_id is required"}, 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    UPDATE loan
                    SET loanstatus_id = %s
                    WHERE loan_id = %s
                      AND memb_id = %s
                      AND loanstatus_id = %s
                    RETURNING loan_id;
                    """,
                    (
                        4,          # cancelled
                        loan_id,
                        member_id,
                        2,          # currently borrowed
                    ),
                )

                loan = cur.fetchone()

                if loan is None:
                    return {
                        "error": "Loan not found or cannot be cancelled"
                    }, 400

            conn.commit()

        return {
            "message": "Loan cancelled",
            "loan_id": loan["loan_id"],
        }, 200

    except Exception:
        return {
            "error": "Failed to update loan"
        }, 500