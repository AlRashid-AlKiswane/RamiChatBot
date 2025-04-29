# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import json
import numpy as np
from typing import Tuple, List, Dict, Any

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
    from dbs import pull_from_table
    from logs import log_debug, log_error, log_info
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

def load_embeddings_and_metadata(
    conn: sqlite3.Connection
) -> Tuple[List[int], np.ndarray, Dict[int, Dict[str, Any]]]:
    """
    Loads embeddings and their associated metadata from the database.

    Args:
        conn (sqlite3.Connection): SQLite connection object.

    Returns:
        Tuple[
            List[int]: IDs list,
            np.ndarray: Embedding vectors,
            Dict[int, Dict[str, Any]]: Metadata dictionary
        ]
    """
    try:
        cursor = conn.cursor()

        # Load embeddings
        embeddings_data = pull_from_table(
            conn, 
            table_name="embeddings", 
            columns=["embedding", "chunk_id"], 
            rely_data="embedding"
        )

        # Load metadata
        metadata_rows = pull_from_table(
            conn, 
            table_name="chunks", 
            columns=["pages", "sources", "authors"], 
            rely_data="metadata"
        )

        ids = []
        embeddings = []

        for record in embeddings_data:
            id_ = record["id"]
            embedding_blob = record["embedding"]

            embedding_list = json.loads(embedding_blob)

            # Convert the list to a NumPy array
            embedding_array = np.array(embedding_list, dtype=np.float32)

            ids.append(id_)
            embeddings.append(embedding_array)

        if not embeddings:
            raise ValueError("No embeddings found.")

        embeddings_array = np.vstack(embeddings).astype(np.float32)

        # Create metadata dict {id: {...}}
        metadata = {
            row["id"]: {
                "page": row["metadata"],
                "source": row["metadata"],
                "author": row["metadata"],
            } for row in metadata_rows
        }

        log_info(f"Loaded {len(ids)} embeddings and {len(metadata)} metadata entries.")

        return ids, np.vstack(embeddings_array), metadata

    except sqlite3.Error as e:
        log_error(f"SQLite error during loading: {e}")
        return [], np.array([]), {}
    except Exception as e:
        log_error(f"Error during loading embeddings and metadata: {e}")
        return [], np.array([]), {}
    finally:
        log_debug("Executed load_embeddings_and_metadata function.")
