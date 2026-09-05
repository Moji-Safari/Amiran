import logging
import os

from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """
    Configure application logging.

    Logs are written to:
        - console
        - logs/app.log
    """

    log_dir = os.path.join(
        app.root_path,
        "..",
        "logs",
    )

    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir,
        "app.log",
    )

    # --------------------------------------------------------
    # Log format
    # --------------------------------------------------------

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # --------------------------------------------------------
    # File handler
    # --------------------------------------------------------

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # --------------------------------------------------------
    # Console handler
    # --------------------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # --------------------------------------------------------
    # Flask logger
    # --------------------------------------------------------

    app.logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logging()
    # is accidentally called more than once.
    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)

    # Don't propagate to the root logger.
    app.logger.propagate = False
