"""
retrieval module for RAG: performs similarity search over stored embeddings.
"""

import logging
import os
import sqlite3
import sys
import traceback
from typing import Any, Dict, List

import numpy as np

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.embedding import EmbeddingModel
    from src.logs import log_debug, log_error, log_info
    from src.enums import RetrievalLogMessages
    from .database_retrieval import load_embeddings_and_metadata
    from .embedding_query import embed_query
    from .faiss_search import build_faiss_index

except (FileNotFoundError, OSError) as e:
    logging.error("Fatal error setting up project directory: %s", str(e))
    logging.error(traceback.format_exc())
    sys.exit(1)


def search(
    query: str,
    embedder: EmbeddingModel,
    conn: sqlite3.Connection,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Search for the most relevant page contents based on a given query.

    Args:
        query (str): The input user query.
        embedder (EmbeddingModel): The embedding model instance to encode the query.
        conn (sqlite3.Connection): SQLite DB connection to retrieve chunked documents.
        top_k (int): Number of top matching results to return.

    Returns:
        List[Dict[str, Any]]: List of matching chunks with 'id' and 'page_content'.

    Raises:
        ImportError: If a dependency import fails.
        RuntimeError: For general unexpected errors.
    """
    try:
        preview = query[:30] + "..." if len(query) > 30 else query
        log_info(RetrievalLogMessages.INFO_SEARCH_START.value.format(preview))

        ids, embeddings_array, _ = load_embeddings_and_metadata(conn)
        if not ids:
            log_error(RetrievalLogMessages.ERR_NO_EMBEDDINGS.value)
            return []

        index = build_faiss_index(embeddings_array)

        vector = embed_query(
            query,
            embedder,
            convert_to_tensor=False,
            normalize_embeddings=False,
        )
        if isinstance(vector, list):
            vector = np.array(vector, dtype=np.float32)

        indices = index.search(np.expand_dims(vector, axis=0), top_k)[1][0]
        log_info(RetrievalLogMessages.INFO_INDICES_RETRIEVED.value.format(len(indices)))

        cursor = conn.cursor()
        results: List[Dict[str, Any]] = []

        for idx in indices:
            if idx < 0:
                continue
            cursor.execute(
                "SELECT id, page_contest FROM chunks WHERE id = ?", (ids[idx],)
            )
            row = cursor.fetchone()
            if row:
                results.append({"id": row[0], "page_content": row[1]})

        return results

    except ImportError as imp_err:
        log_error(RetrievalLogMessages.ERR_IMPORT_ERROR.value.format(str(imp_err)))
        raise ImportError(
            RetrievalLogMessages.RAISE_IMPORT_ERROR.value.format(str(imp_err))
        ) from imp_err

    except sqlite3.Error as db_err:
        log_error(RetrievalLogMessages.ERR_DB_ERROR.value.format(str(db_err)))
        return []

    except Exception as err:
        log_error(RetrievalLogMessages.ERR_GENERAL_ERROR.value.format(str(err)))
        raise RuntimeError(
            RetrievalLogMessages.RAISE_GENERAL_ERROR.value.format(str(err))
        ) from err

    finally:
        log_debug(RetrievalLogMessages.DEBUG_EXEC_COMPLETE.value)
