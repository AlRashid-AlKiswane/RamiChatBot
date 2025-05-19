import logging
import os
import sys
import sqlite3


FILE_LOCATION = f"{os.path.dirname(__file__)}/create_taples.py"

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

def create_chunks_table(conn: sqlite3.Connection):
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_contest INTEGER NOT NULL,
                pages TEXT NOT NULL,
                sources TEXT NOT NULL,
                authors TEXT NOT NULL
            );
        """)
        conn.commit()
        log_info("Table 'chunks' created successfully.")
    except Exception as e:
        log_error(f"Error creating 'chunks' table: {e}")
        raise



def create_embeddings_table(conn: sqlite3.Connection):
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                FOREIGN KEY(chunk_id) REFERENCES chunks(id)
            );
        """)
        log_info("Table 'embeddings' created successfully.")
    except Exception as e:
        log_error(f"Error creating 'embeddings' table: {e}")
        raise


def create_query_responses_table(conn: sqlite3.Connection):
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL
            );
        """)
        log_info("Table 'query_responses' created successfully.")
    except Exception as e:
        log_error(f"Error creating 'query_responses' table: {e}")
        raise
