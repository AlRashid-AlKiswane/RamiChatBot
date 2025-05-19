import logging
import os
import sys
import sqlite3


# Add root dir and handle potential import errors
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
    from helpers import get_settings, Settings
except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

app_setting: Settings = get_settings()

def create_sqlite_engine():
    """
    Creates a connection to an SQLite database.
    If the database does not exist, it will be created.
    """
    try:
        # Create a connection to the SQLite database
        conn = sqlite3.connect(database=app_setting.DATABASE_URL)
        log_info(f"Successfully connected to the database: {app_setting.DATABASE_URL}")
        return conn
    except Exception as e:
        log_error(f"Filed to connect to the database: {e}")
        raise
