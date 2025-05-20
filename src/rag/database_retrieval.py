"""
database_retrieval module: Load embeddings and metadata from SQLite database.

This module provides functionality to retrieve vector embeddings and their
associated metadata from an SQLite database. It includes robust error handling
and logging support to ensure reliability during database operations.
"""

import os
import sqlite3
import logging
import json
import sys
import traceback
from typing import Tuple, List, Dict, Any

import numpy as np

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_debug, log_error, log_info
    from src.dbs import pull_from_table
    from src.enums import DBRetrievalMessages

except (FileNotFoundError, OSError) as e:
    logging.error("Fatal error setting up project directory: %s", str(e))
    logging.error(traceback.format_exc())
    sys.exit(1)


def load_embeddings_and_metadata(
    conn: sqlite3.Connection,
) -> Tuple[List[int], np.ndarray, Dict[int, Dict[str, Any]]]:
    """
    Load vector embeddings and their corresponding metadata from the SQLite database.

    This function queries two tables: 'embeddings' for vector data and 'chunks' for
    metadata about each chunk. It deserializes the embeddings from JSON blobs,
    converts them to numpy arrays, and aggregates metadata in a dictionary keyed
    by chunk IDs.

    Args:
        conn (sqlite3.Connection): An active SQLite connection object.

    Returns:
        Tuple containing:
            - List[int]: List of chunk IDs.
            - np.ndarray: 2D array of embeddings (shape: number_of_chunks x embedding_dim).
            - Dict[int, Dict[str, Any]]: Dictionary mapping chunk ID to metadata dictionary.

    Raises:
        sqlite3.Error: If a database access error occurs.
        ValueError: If no embeddings are found in the database.
        json.JSONDecodeError: If embedding JSON decoding fails.
    """
    log_info(DBRetrievalMessages.LOAD_START.value)

    try:
        embeddings_data = pull_from_table(
            conn,
            table_name="embeddings",
            columns=["id", "embedding"],
            rely_data="embedding",
        )

        metadata_rows = pull_from_table(
            conn,
            table_name="chunks",
            columns=["id", "page", "source", "author"],
            rely_data="metadata",
        )

        ids: List[int] = []
        embeddings_list: List[np.ndarray] = []

        for record in embeddings_data:
            id_ = record["id"]
            embedding_blob = record["embedding"]

            # Decode JSON string to list
            embedding_list = json.loads(embedding_blob)

            # Convert list to numpy array of float32
            embedding_array = np.array(embedding_list, dtype=np.float32)

            ids.append(id_)
            embeddings_list.append(embedding_array)

        if not embeddings_list:
            raise ValueError(DBRetrievalMessages.NO_EMBEDDINGS_FOUND.value)

        embeddings_array = np.vstack(embeddings_list)

        metadata: Dict[int, Dict[str, Any]] = {
            row["id"]: {
                "page": row["page"],
                "source": row["source"],
                "author": row["author"],
            }
            for row in metadata_rows
        }

        log_info(DBRetrievalMessages.LOAD_SUCCESS.value.format(len(ids), len(metadata)))
        return ids, embeddings_array, metadata

    except sqlite3.Error as sql_err:
        log_error(DBRetrievalMessages.SQLITE_ERROR.value.format(sql_err))
        raise
    except (ValueError, json.JSONDecodeError) as data_err:
        log_error(DBRetrievalMessages.DATA_ERROR.value.format(data_err))
        raise
    except Exception as exc:
        log_error(f"Unexpected error in load_embeddings_and_metadata: {exc}")
        raise
    finally:
        log_debug(DBRetrievalMessages.FUNCTION_COMPLETED.value)
