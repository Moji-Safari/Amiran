from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.auth.route import ROLE_LIBRARIAN, ROLE_MEMBER, role_required
from db.database import get_db

loan_bp = Blueprint("loan", __name__, url_prefix="/loan")



@loan_bp.route("/borrow", methods=["POST"])
@jwt_required()
@role_required(ROLE_MEMBER)
def create_request():
    user = get_jwt_identity()

    user_branch = user.branch_id
    member_id = user.user_id
    book_id = request.args.get("book_id", type=int)

    if book_id is None:
        return {"error": "book_id is required"}, 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO loan (
                        branch_id,
                        book_id,
                        loanstatus_id,
                        member_id
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING loan_id;
                    """,
                    (
                        user_branch,
                        book_id,
                        1,          # pending status
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
        conn.rollback()
        return {"error": "Failed to create loan request"}, 500

#for cancel operation we can use DELETE method and <int:x>



@loan_bp.route("/approved/<int:state>", methods=["GET", "POST"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def pending_operations():

    if request.method == "GET":
        with get_db() as conn:
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


