from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.auth.route import role_required
from db.database import get_db

loan_bp = Blueprint("member", __name__, url_prefix="/member")
