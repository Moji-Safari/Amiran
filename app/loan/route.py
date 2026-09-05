from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.auth.route import role_required
from db.database import get_db


loan_bp = Blueprint("loan", __name__, url_prefix="/loan")



loan_bp.route("/borrow", methods=["GET"])
@jwt_required()
@role_required("MEMBER")
def create_request():
    user = get_jwt_identity()
    user_branch = user.branch_id
    book_id = request.args.get('book_id',type=int)

    try:

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO TABLE loan(user_branch,book_id,loanstatus_id,user,
                    
                    ) VALUES(
                    %s,%s,%s,%s)

                  
                    """
                )
