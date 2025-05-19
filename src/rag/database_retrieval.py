"""
database_retrieval module: load embeddings and metadata from SQLite.
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
    
except (FileNotFoundError, OSError) as e:
    logging.error("Fatal error setting up project directory: %s", str(e))
    logging.error(traceback.format_exc())
    sys.exit(1)

def load_embeddings_and_metadata(
    conn: sqlite3.Connection
) -> Tuple[List[int], np.ndarray, Dict[int, Dict[str, Any]]]:
    """
    Load embeddings and their associated metadata from the database.

    Args:
        conn: SQLite connection object.

    Returns:
        ids: List of chunk IDs.
        embeddings_array: 2D numpy array of embeddings.
        metadata: Mapping from chunk ID to its metadata dict.
    """
    try:
        # Load embeddings records
        embeddings_data = pull_from_table(
            conn,
            table_name="embeddings",
            columns=["id", "embedding"],
            rely_data="embedding",
        )

        # Load metadata records
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
            embedding_list = json.loads(embedding_blob)
            embedding_array = np.array(embedding_list, dtype=np.float32)

            ids.append(id_)
            embeddings_list.append(embedding_array)

        if not embeddings_list:
            raise ValueError("No embeddings found in the database.")

        embeddings_array = np.vstack(embeddings_list)

        # Build metadata dict
        metadata: Dict[int, Dict[str, Any]] = {
            row["id"]: {
                "page": row["page"],
                "source": row["source"],
                "author": row["author"],
            }
            for row in metadata_rows
        }

        log_info(f"database_retrieval.load_embeddings_and_metadata: "
                 f"Loaded {len(ids)} embeddings and {len(metadata)} metadata entries.")
        return ids, embeddings_array, metadata

    except sqlite3.Error as sql_err:
        log_error(f"database_retrieval.load_embeddings_and_metadata - SQLite error: {sql_err}")
    except (ValueError, json.JSONDecodeError) as data_err:
        log_error(f"database_retrieval.load_embeddings_and_metadata - Data error: {data_err}")
    finally:
        log_debug("database_retrieval.load_embeddings_and_metadata: Function execution completed.")

    # Return empty defaults on error
    return [], np.array([], dtype=np.float32), []
