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
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from config import get_settings, Settings
    from schemes import Chunk, Embedding, QueryResponse
except Exception as e:
    msg = f"Import Error in: {FILE_LOCATION}, Error: {e}"
    raise ImportError(msg)

app_setting: Settings = get_settings()

def insert_chunk(conn: sqlite3.Connection, data: pd.DataFrame):
    """
    Inserts a DataFrame of chunks (with page_counten, pages, sources, authors) into the 'chunks' table.
    """
    cursor = conn.cursor()

    try:
        data.to_sql("chunks", conn, if_exists='append', index=False)

        conn.commit()
        conn.close()
        log_info(f"Inserted {len(data)} chunk(s) into 'chunks' table.")
    except Exception as e:
        log_error(f"Error inserting chunk(s): {e}")
        conn.rollback()


def insert_embedding(conn: sqlite3.Connection, embedding: Embedding):
    """
    Inserts an embedding into the 'embeddings' table after validation.
    """
    cursor = conn.cursor()
    try:
        # Validate the embedding data with Pydantic
        embedding_data = embedding.dict()
        cursor.execute("""
            INSERT INTO embeddings (chunk_id, embedding)
            VALUES (?, ?)
        """, (embedding_data['chunk_id'], embedding_data['embedding']))
        conn.commit()
        log_info(f"Inserted embedding for chunk_id: {embedding_data['chunk_id']}")
    except ValidationError as ve:
        log_error(f"Validation failed for embedding: {ve}")
    except Exception as e:
        log_error(f"Error inserting embedding: {e}")
        conn.rollback()


def insert_query_response(conn: sqlite3.Connection, query_response: QueryResponse):
    """
    Inserts a query-response pair into the 'query_responses' table after validation.
    """
    cursor = conn.cursor()
    try:
        # Validate the query-response data with Pydantic
        query_response_data = query_response.dict()
        cursor.execute("""
            INSERT INTO query_responses (query, response)
            VALUES (?, ?)
        """, (query_response_data['query'], query_response_data['response']))
        conn.commit()
        log_info(f"Inserted query-response pair: Query: {query_response_data['query']}, Response: {query_response_data['response']}")
    except ValidationError as ve:
        log_error(f"Validation failed for query-response pair: {ve}")
    except Exception as e:
        log_error(f"Error inserting query-response pair: {e}")
        conn.rollback()
