import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def setup_logging() -> None:
    """
    Configure application-wide logging.

    Logging is intentionally kept simple and centralized so
    services and API routes use the same configuration.
    """

    root_logger = logging.getLogger()

    # Avoid adding duplicate handlers when the application
    # reloads under Uvicorn.
    if root_logger.handlers:
        return

    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(
        sys.stdout
    )

    formatter = logging.Formatter(
        LOG_FORMAT
    )

    handler.setFormatter(
        formatter
    )

    root_logger.addHandler(
        handler
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger for a module/service.
    """

    return logging.getLogger(name)