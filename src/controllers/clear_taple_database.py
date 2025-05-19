import logging
import os
import sys
import sqlite3

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


def clear_table(conn: sqlite3.Connection, table_name: str) -> None:
    """
    Clears all records from the specified SQLite table.

    Args:
        conn (sqlite3.Connection): An active database connection.
        table_name (str): The name of the table to clear.

    Raises:
        ValueError: If table name contains suspicious characters.
        Exception: If an unexpected error occurs during deletion.
    """
    if not table_name.isidentifier():
        log_error(f"Invalid table name: {table_name}")
        raise ValueError("Invalid table name. Must be a valid SQL identifier.")

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name};")
        conn.commit()
        log_info(f"All records deleted from table '{table_name}'.")

    except sqlite3.Error as e:
        log_error(f"SQLite error while deleting from '{table_name}': {e}")
    except Exception as e:
        log_error(f"Unexpected error clearing table '{table_name}': {e}")
        raise
    finally:
        if cursor:
            cursor.close()