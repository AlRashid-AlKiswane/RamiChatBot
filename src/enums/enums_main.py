"""
main_app_log_messages module.

Defines structured logging messages for application startup, shutdown,
and request validation events in a FastAPI-based application. This helps
ensure consistent and readable log outputs, improving debugging and
monitoring throughout the application lifecycle.

Usage:
    Use the MainAppLogMessages enum to reference standardized log messages
    during application startup, shutdown, and request validation error handling.
"""

from enum import Enum


class MainAppLogMessages(Enum):
    """
    Enum for structured log messages in the FastAPI main application lifecycle.

    This enumeration contains categorized messages for:

    - Application startup events.
    - Graceful or failed shutdown procedures.
    - Request validation error logging.

    Attributes:
        STARTUP_BEGIN (str): Message indicating the FastAPI app is initializing.
        STARTUP_SUCCESS (str): Message indicating successful initialization.
        STARTUP_FAIL (str): Message prefix for failed startup (append error detail).
        SHUTDOWN_BEGIN (str): Message indicating the app is beginning to shut down.
        SHUTDOWN_DB_CLOSED (str): Message confirming SQLite connection was closed.
        SHUTDOWN_FAIL (str): Message prefix for shutdown failure (append error detail).
        VALIDATION_FAIL (str): Message prefix for request validation failures (append error detail).
    """

    STARTUP_BEGIN = "[STARTUP] Initializing FastAPI app..."
    STARTUP_SUCCESS = "[STARTUP] Initialization completed successfully."
    STARTUP_FAIL = "[STARTUP] Initialization failed:"
    SHUTDOWN_BEGIN = "[SHUTDOWN] Shutting down FastAPI app..."
    SHUTDOWN_DB_CLOSED = "[SHUTDOWN] SQLite connection closed."
    SHUTDOWN_FAIL = "[SHUTDOWN] Error during shutdown:"
    VALIDATION_FAIL = "[VALIDATION ERROR] Request validation failed:"
