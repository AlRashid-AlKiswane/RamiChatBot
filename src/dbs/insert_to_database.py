import logging
import os
import sys
import sqlite3
import json
import pandas as pd

from pydantic import ValidationError

FILE_LOCATION = f"{os.path.dirname(__file__)}/inset_to_database.py"

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

def insert_chunk(conn: sqlite3.Connection, data: pd.DataFrame):
    """
    Inserts a DataFrame of chunks (with page_counten, pages, sources, authors) into the 'chunks' table.
    """

    try:
        data.to_sql("chunks", conn, if_exists='append', index=False)

        conn.commit()
        log_info(f"Inserted {len(data)} chunk(s) into 'chunks' table.")
    except sqlite3.DatabaseError as db_err:
        log_error(f"Database error while inserting chunk(s): {db_err}")
        conn.rollback()
    except Exception as e:
        log_error(f"Unexpected error while inserting chunk(s): {e}")
        conn.rollback()


def insert_embedding(conn: sqlite3.Connection, embedding: list, chunk_id: str):
    """
    Inserts an embedding into the 'embeddings' table after validation.
    """
    cursor = conn.cursor()
    try:
        # Serialize embedding list to JSON string
        embedding_json = json.dumps(embedding)
        
        cursor.execute("""
            INSERT INTO embeddings (chunk_id, embedding)
            VALUES (?, ?)
        """, (chunk_id, embedding_json))

        conn.commit()
        log_info(f"Inserted embedding for chunk_id: {chunk_id}")
    except ValidationError as ve:
        log_error(f"Validation failed for embedding: {ve}")
    except Exception as e:
        log_error(f"Error inserting embedding: {e}")
        conn.rollback()


def insert_query_response(conn: sqlite3.Connection, query, response, user_id: str):
    """
    Inserts a query-response pair into the 'query_responses' table after validation.
    """
    try:
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")
        if not isinstance(response, str):
            raise ValueError("Response must be a string.")
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string.")
    except ValueError as ve:
        log_error(f"Validation failed for query-response pair: {ve}")
        return
    except Exception as e:
        log_error(f"Error validating query-response pair: {e}")
        return
    # If validation passes, proceed to insert into the database
    # Ensure the connection is open
    if conn is None:
        log_error("Database connection is not established.")
        return
    
    # Create a cursor object
    cursor = conn.cursor()
    try:
        # Validate the query-response data with Pydantic
        cursor.execute("""
            INSERT INTO query_responses (user_id, query, response)
            VALUES (?, ?, ?)
        """, (user_id, query, response))

        conn.commit()

    except ValidationError as ve:
        log_error(f"Validation failed for query-response pair: {ve}")
    except Exception as e:
        log_error(f"Error inserting query-response pair: {e}")
        conn.rollback()
