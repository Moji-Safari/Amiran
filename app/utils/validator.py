import re
from datetime import date, datetime

from config import (
    Config,
)


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def get_extension(filename):
    """
    Return the file extension without the leading dot.
    """
    if not filename or "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1].lower()


def validate_required(data, fields):
    """
    Check that all required fields exist and are not None.
    """
    for field in fields:
        if field not in data or data[field] is None:
            return f"{field} is required"

    return None


def validate_int(
    value,
    field_name,
    min_value=None,
    max_value=None,
):
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
    if not isinstance(value, str):
        return f"{field_name} must be a string"

    if min_length is not None and len(value.strip()) < min_length:
        return f"{field_name} must be at least {min_length} characters"

    if max_length is not None and len(value) > max_length:
        return f"{field_name} must be at most {max_length} characters"

    return None


def validate_email(email):
    if not isinstance(email, str):
        return "email must be a string"

    email = email.strip()

    if len(email) > 255:
        return "email must be at most 255 characters"

    if not EMAIL_PATTERN.fullmatch(email):
        return "email must be a valid email address"

    return None


def validate_positive_id(value, field_name):
    return validate_int(
        value,
        field_name,
        min_value=1,
    )


def validate_date_value(value, field_name):
    if not isinstance(value, str):
        return (
            f"{field_name} must be a date in YYYY-MM-DD format"
        )

    try:
        date.fromisoformat(value)
    except ValueError:
        return (
            f"{field_name} must be a valid date "
            "in YYYY-MM-DD format"
        )

    return None


def validate_datetime_value(value, field_name):
    if not isinstance(value, str):
        return f"{field_name} must be a valid datetime"

    try:
        datetime.fromisoformat(value)
    except ValueError:
        return f"{field_name} must be a valid datetime"

    return None


def validate_borrow_request(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    error = validate_required(data, ["book_id"])

    if error:
        return error

    error = validate_positive_id(
        data["book_id"],
        "book_id",
    )

    if error:
        return error

    return None


def validate_member_data(data, partial=False):
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

    if "branch_id" in data and data["branch_id"] is not None:
        error = validate_positive_id(
            data["branch_id"],
            "branch_id",
        )

        if error:
            return error

    for field in ("first_name", "last_name"):
        if field in data:
            error = validate_string(
                data[field],
                field,
                min_length=1,
                max_length=100,
            )

            if error:
                return error

    if "email" in data:
        error = validate_email(data["email"])

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

    if "membership_type" in data:
        error = validate_string(
            data["membership_type"],
            "membership_type",
            min_length=1,
            max_length=50,
        )

        if error:
            return error

    return None


def validate_loan_status_update(data):
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
    # Cover is optional.
    if file is None:
        return None

    if not file.filename:
        return "cover filename is required"

    extension = get_extension(file.filename)

    if extension not in Config.ALLOWED_IMAGE_EXTENSIONS:
        return "cover must be JPG, JPEG, PNG, or WEBP"

    if file.content_type not in Config.ALLOWED_MIME_TYPES:
        return "invalid cover content type"

    return None