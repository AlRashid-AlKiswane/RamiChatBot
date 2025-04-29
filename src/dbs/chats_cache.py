import os
import sys
import sqlite3
import json
import pandas as pd

from pydantic import ValidationError

FILE_LOCATION = f"{os.path.dirname(__file__)}/chatas_cache.py"

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


def create_cache_table(conn: sqlite3.Connection):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_cache (
                user_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                PRIMARY KEY (user_id, query)
            )
        """)
        conn.commit()
        log_info("Chat cache table created or already exists.")
    except Exception as e:
        log_error(f"[CACHE ERROR] Failed to create table: {e}")


def get_cached_response(conn: sqlite3.Connection, user_id: str, query: str):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT response FROM chat_cache WHERE user_id = ? AND query = ?
        """, (user_id, query))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        log_error(f"[CACHE ERROR] Fetching cache failed: {e}")
        return None


def insert_cached_response(conn: sqlite3.Connection, user_id: str, query: str, response: str):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO chat_cache (user_id, query, response)
            VALUES (?, ?, ?)
        """, (user_id, query, response))
        conn.commit()
        log_info(f"[CACHE] Cached response inserted for query: {query}")
    except Exception as e:
        log_error(f"[CACHE ERROR] Inserting cache failed: {e}")
        conn.rollback()