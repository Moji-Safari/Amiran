from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required
from app.auth.route import ROLE_LIBRARIAN, ROLE_MEMBER, role_required

from app.auth.constants import ROLE_LIBRARIAN
from app.auth.decorators import role_required
from app.utils.file_storage import save_cover
from app.utils.validator import validate_cover
from app.db.database import get_db


book_bp = Blueprint(
    "books",
    __name__,
    url_prefix="/books",
)


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

@book_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def create_book():

    title = request.form.get("title")
    isbn = request.form.get("isbn")
    publication_year = request.form.get(
        "publication_year",
        type=int,
    )
    genre = request.form.get("genre")

    if not title:
        return {"error": "title is required"}, 400

    if len(title) > 255:
        return {
            "error": "title must be at most 255 characters"
        }, 400

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
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING book_id
                    """,
                    (
                        title,
                        isbn,
                        publication_year,
                        genre,
                        cover_filename,
                    ),
                )

                book_id = cur.fetchone()["book_id"]

            conn.commit()

        return {
            "message": "Book created",
            "book_id": book_id,
        }, 201

    except Exception:
        current_app.logger.exception(
            "Failed to create book"
        )

        return {
            "error": "Failed to create book"
        }, 500


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

@book_bp.route("/", methods=["GET"])
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
                        isbn,
                        publication_year,
                        genre,
                        added_at,
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
        current_app.logger.exception(
            "Failed to retrieve books"
        )

        return {
            "error": "Failed to retrieve books"
        }, 500


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

@book_bp.route("/<int:book_id>", methods=["GET"])
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
                        isbn,
                        publication_year,
                        genre,
                        added_at,
                        cover_path
                    FROM books
                    WHERE book_id = %s
                    """,
                    (book_id,),
                )

                book = cur.fetchone()

        if book is None:
            return {
                "error": "Book not found"
            }, 404

        return book, 200

    except Exception:
        current_app.logger.exception(
            "Failed to retrieve book"
        )

        return {
            "error": "Failed to retrieve book"
        }, 500


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

@book_bp.route("/<int:book_id>", methods=["PATCH"])
@jwt_required()
@role_required(ROLE_LIBRARIAN)
def update_book(book_id):

    title = request.form.get("title")
    isbn = request.form.get("isbn")
    publication_year = request.form.get(
        "publication_year",
        type=int,
    )
    genre = request.form.get("genre")

    cover = request.files.get("cover")

    # ---------------------------------------------
    # Validate supplied fields
    # ---------------------------------------------

    if title is not None:

        if not title:
            return {
                "error": "title cannot be empty"
            }, 400

        if len(title) > 255:
            return {
                "error": "title must be at most 255 characters"
            }, 400

    if publication_year is not None:

        if publication_year <= 0:
            return {
                "error": "publication_year must be positive"
            }, 400

    if cover is not None:

        error = validate_cover(cover)

        if error:
            return {
                "error": error
            }, 400

    try:

        with get_db() as conn:

            with conn.cursor() as cur:

                # ---------------------------------------------
                # Check that book exists
                # ---------------------------------------------

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
                    return {
                        "error": "Book not found"
                    }, 404

                # ---------------------------------------------
                # Save new cover if supplied
                # ---------------------------------------------

                new_cover_filename = None

                if cover is not None:
                    new_cover_filename = save_cover(cover)

                # ---------------------------------------------
                # Update only supplied fields
                # ---------------------------------------------

                cur.execute(
                    """
                    UPDATE books
                    SET
                        title = COALESCE(%s, title),
                        isbn = COALESCE(%s, isbn),
                        publication_year = COALESCE(
                            %s,
                            publication_year
                        ),
                        genre = COALESCE(%s, genre),
                        cover_path = COALESCE(
                            %s,
                            cover_path
                        )
                    WHERE book_id = %s
                    """,
                    (
                        title,
                        isbn,
                        publication_year,
                        genre,
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

        current_app.logger.exception(
            "Failed to update book"
        )

        return {
            "error": "Failed to update book"
        }, 500


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

@book_bp.route("/<int:book_id>", methods=["DELETE"])
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
            return {
                "error": "Book not found"
            }, 404

        return {
            "message": "Book deleted",
            "book_id": deleted["book_id"],
        }, 200

    except Exception:

        current_app.logger.exception(
            "Failed to delete book"
        )

        return {
            "error": "Failed to delete book"
        }, 500