import os
import uuid

from flask import current_app

from app.utils.validator import get_extension


def save_cover(file):
    """
    Generate a unique filename and save the uploaded file.
    """
    extension = get_extension(file.filename)

    filename = f"{uuid.uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(
        upload_folder,
        exist_ok=True,
    )

    file_path = os.path.join(
        upload_folder,
        filename,
    )

    file.save(file_path)

    return filename