
import os
import re
from datetime import date, datetime
import uuid

from flask import current_app

from app.books.route import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, get_extension

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_required(data, fields):
    """
    Check that all required fields exist and are not empty.
    Returns an error message or None.
    """
    for field in fields:
        if field not in data or data[field] is None:
            return f"{field} is required"

    return None


def validate_int(value, field_name, min_value=None, max_value=None):
    """
    Validate an integer and optionally its range.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        return f"{field_name} must be an integer"

    if min_value is not None and value < min_value:
        return f"{field_name} must be at least {min_value}"

    if max_value is not None and value > max_value:
        return f"{field_name} must be at most {max_value}"

    return None


def validate_string(
    value,
    field_name,
    min_length=None,
    max_length=None,
):
    """
    Validate a string and optionally its length.
    """
    if not isinstance(value, str):
        return f"{field_name} must be a string"

    if min_length is not None and len(value) < min_length:
        return f"{field_name} must be at least {min_length} characters"

    if max_length is not None and len(value) > max_length:
        return f"{field_name} must be at most {max_length} characters"

    return None


def validate_email(email):
    """
    Validate email format.
    """
    if not isinstance(email, str):
        return "email must be a string"

    if not EMAIL_PATTERN.match(email):
        return "email must be a valid email address"

    if len(email) > 255:
        return "email must be at most 255 characters"

    return None


def validate_positive_id(value, field_name):
    """
    Validate an ID such as book_id, member_id, branch_id, etc.
    """
    return validate_int(
        value,
        field_name,
        min_value=1,
    )


def validate_date_value(value, field_name):
    """
    Validate a date value.
    """
    if not isinstance(value, str):
        return f"{field_name} must be a date in YYYY-MM-DD format"

    try:
        date.fromisoformat(value)
    except ValueError:
        return f"{field_name} must be a valid date in YYYY-MM-DD format"

    return None


def validate_datetime_value(value, field_name):
    """
    Validate an ISO 8601 datetime string.
    """
    if not isinstance(value, str):
        return f"{field_name} must be a valid datetime"

    try:
        datetime.fromisoformat(value)
    except ValueError:
        return f"{field_name} must be a valid datetime"

    return None


def validate_borrow_request(data):
    """
    Validate the data required to create a borrowing request.
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    error = validate_required(
        data,
        ["book_id"],
    )

    if error:
        return error

    error = validate_positive_id(
        data["book_id"],
        "book_id",
    )

    if error:
        return error

    return None


def validate_member_data(data):
    """
    Validate member creation/update data.
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    error = validate_required(
        data,
        [
            "first_name",
            "last_name",
            "email",
            "membership_type",
        ],
    )

    if error:
        return error

    error = validate_string(
        data["first_name"],
        "first_name",
        min_length=1,
        max_length=100,
    )

    if error:
        return error

    error = validate_string(
        data["last_name"],
        "last_name",
        min_length=1,
        max_length=100,
    )

    if error:
        return error

    error = validate_email(data["email"])

    if error:
        return error

    error = validate_string(
        data["membership_type"],
        "membership_type",
        min_length=1,
        max_length=50,
    )

    if error:
        return error

    if "phone" in data and data["phone"] is not None:
        error = validate_string(
            data["phone"],
            "phone",
            max_length=50,
        )

        if error:
            return error

    if "branch_id" in data and data["branch_id"] is not None:
        error = validate_positive_id(
            data["branch_id"],
            "branch_id",
        )

        if error:
            return error

    return None


def validate_loan_status_update(data):
    """
    Validate a request that changes a loan's status.
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    error = validate_required(
        data,
        ["loan_id", "status_id"],
    )

    if error:
        return error

    error = validate_positive_id(
        data["loan_id"],
        "loan_id",
    )

    if error:
        return error

    error = validate_positive_id(
        data["status_id"],
        "status_id",
    )

    if error:
        return error

    return None

def validate_cover(file):
    """
    Validate the uploaded book cover.

    Returns:
        None if valid
        error message if invalid
    """

    if file is None:
        return "cover is required"

    if not file.filename:
        return "cover filename is required"

    # 1. Extension allowlist
    extension = get_extension(file.filename)

    if extension not in ALLOWED_EXTENSIONS:
        return "cover must be JPG, JPEG, PNG, or WEBP"

    # 2. MIME type allowlist
    if file.content_type not in ALLOWED_MIME_TYPES:
        return "invalid cover content type"

    return None


def save_cover(file):
    """
    Generate a safe filename and save the uploaded file.
    """

    extension = get_extension(file.filename)

    filename = f"{uuid.uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)

    file.save(file_path)

    return filename
