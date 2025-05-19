import logging
import os
import sys
import sqlite3
from typing import List, Optional, Dict, Any, Union, Tuple


try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

def pull_from_table(
    conn: sqlite3.Connection,
    table_name: str,
    rely_data: str = "text",
    cach: Optional[Tuple[str, str]] = None,  # Tuple[user_id, query]
    columns: Optional[List[str]] = None,
) -> Union[List[Dict[str, Any]], Optional[str]]:
    """
    Pulls data from a specified table or retrieves a cached response.

    Args:
        conn (sqlite3.Connection): SQLite connection.
        table_name (str): Target table name.
        columns (List[str]): List of column names to select.
        rely_data (str): Key name for data in return dictionary.
        cach (Optional[Tuple[str, str]]): If set, retrieves cached response for (user_id, query).

    Returns:
        - List[Dict[str, Any]] for general table fetch.
        - str or None for cache mode (cached response).
    """
    try:
        cursor = conn.cursor()

        # Cache mode
        if cach:
            user_id, query = cach
            cursor.execute(
                "SELECT response FROM query_responses WHERE user_id = ? AND query = ?",
                (user_id, query)
            )
            row = cursor.fetchone()
            log_info(f"[CACHE MODE] Queried cache for user_id={user_id}, query='{query}'. Found: {bool(row)}")
            return row[0] if row else None

        # General fetch mode
        else:
            cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
            rows = cursor.fetchall()
            log_info(f"Pulled {len(rows)} row(s) from table '{table_name}'.")

            result = [
                {"id": row[1], rely_data: row[0]} for row in rows
            ]
            return result

    except Exception as e:
        log_error(f"Failed to pull data from '{table_name}': {e}")
        return None if cach else []
    finally:
        log_debug("Executed pull_from_table.")
