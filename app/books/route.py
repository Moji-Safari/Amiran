
import os
import uuid

from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required

from app.utils.validator import save_cover, validate_cover
from auth.decorators import role_required
from auth.constants import ROLE_LIBRARIAN
from db.database import get_db


book_bp = Blueprint("books", __name__, url_prefix="/books")


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def get_extension(filename):
    """
    Return the file extension without the dot.
    """
    if "." not in filename:
        return None

    return filename.rsplit(".", 1)[1].lower()




# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

@book_bp.route("/create", methods=["POST"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def create_book():

    title = request.form.get("title")
    isbn = request.form.get("isbn")
    publc_yr = request.form.get("publication_year", type=int)
    genre=request.form.get("genre")


    if not title:
        return {"error": "title is required"}, 400

    if len(title) > 255:
        return {"error": "title must be at most 255 characters"}, 400

    

    cover = request.files.get("cover")

    error = validate_cover(cover)

    if error:
        return {"error": error}, 400

    try:
        cover_filename = save_cover(cover)

        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO books (
                        title,
                        isbn,
                        publication_year,
                        genre,
                        cover_path

                    )
                    VALUES (%s, %s, %s,%s,%s)
                    RETURNING book_id
                    """,
                    (
                        title,
                        isbn,
                        publc_yr,
                        genre,
                        cover_filename

                    ),
                )

                book_id = cur.fetchone()["book_id"]

            conn.commit()

        return {
            "message": "Book created",
            "book_id": book_id,
        }, 201

    except Exception:
        return {
            "error": "Failed to create book"
        }, 500


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

@book_bp.route("/find/lst", methods=["GET"])
@jwt_required()
def get_books():

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        book_id,
                        title,
                        cover_path
                    FROM books
                    ORDER BY book_id
                    """
                )

                books = cur.fetchall()

        return {
            "books": books
        }, 200

    except Exception:
        return {
            "error": "Failed to retrieve books"
        }, 500


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

@book_bp.route("/find/<int:book_id>", methods=["GET"])
@jwt_required()
def get_book(book_id):

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        book_id,
                        title,
                        cover_path
                    FROM books
                    WHERE book_id = %s
                    """,
                    (book_id,),
                )

                book = cur.fetchone()

        if book is None:
            return {"error": "Book not found"}, 404

        return book, 200

    except Exception:
        return {
            "error": "Failed to retrieve book"
        }, 500


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

@book_bp.route("/update/<int:book_id>", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def update_book(book_id):

    title = request.form.get("title")
    author_id = request.form.get("author_id", type=int)
    cover = request.files.get("cover")

    if title is not None:

        if not title:
            return {"error": "title cannot be empty"}, 400

        if len(title) > 255:
            return {
                "error": "title must be at most 255 characters"
            }, 400

    if author_id is not None and author_id <= 0:
        return {
            "error": "author_id must be a positive integer"
        }, 400

    if cover is not None:

        error = validate_cover(cover)

        if error:
            return {"error": error}, 400

    try:

        with get_db() as conn:
            with conn.cursor() as cur:

                # Check that book exists
                cur.execute(
                    """
                    SELECT cover_path
                    FROM books
                    WHERE book_id = %s
                    """,
                    (book_id,),
                )

                existing_book = cur.fetchone()

                if existing_book is None:
                    return {"error": "Book not found"}, 404

                new_cover_filename = None

                if cover is not None:
                    new_cover_filename = save_cover(cover)

                # Update only supplied fields
                cur.execute(
                    """
                    UPDATE books
                    SET
                        title = COALESCE(%s, title),
                        cover_path = COALESCE(
                            %s,
                            cover_path
                        )
                    WHERE book_id = %s
                    """,
                    (
                        title,
                        new_cover_filename,
                        book_id,
                    ),
                )

            conn.commit()

        return {
            "message": "Book updated",
            "book_id": book_id,
        }, 200

    except Exception:
        return {
            "error": "Failed to update book"
        }, 500


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

@book_bp.route("/update/<int:book_id>", methods=["DELETE"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def delete_book(book_id):

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    DELETE FROM books
                    WHERE book_id = %s
                    RETURNING book_id
                    """,
                    (book_id,),
                )

                deleted = cur.fetchone()

            conn.commit()

        if deleted is None:
            return {"error": "Book not found"}, 404

        return {
            "message": "Book deleted",
            "book_id": deleted["book_id"],
        }, 200

    except Exception:
        return {
            "error": "Failed to delete book"
        }, 500

