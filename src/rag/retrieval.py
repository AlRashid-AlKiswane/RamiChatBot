"""
retrieval module for RAG: perform similarity search over stored embeddings.
"""

import sqlite3
from typing import Any, Dict, List

import numpy as np

from src.embedding import EmbeddingModel
from src.logs import log_debug, log_error, log_info
from .database_retrieval import load_embeddings_and_metadata
from .embedding_query import embed_query
from .faiss_search import build_faiss_index

# pylint: disable=too-many-locals
def search(
    query: str,
    embedder: EmbeddingModel,
    conn: sqlite3.Connection,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Search for the most relevant page contents based on the query.

    Args:
        query: The input query string.
        embedder: The embedding model instance.
        conn: The SQLite database connection.
        top_k: Number of top similar entries to return.

    Returns:
        A list of dicts with 'id' and 'page_content'.
    """
    try:
        preview = query[:30] + "..." if len(query) > 30 else query
        log_info(f"search: Starting search for query: {preview}")

        ids, embeddings_array, _ = load_embeddings_and_metadata(conn)
        if not ids:
            log_error("search: No embeddings in database.")
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
        log_info(f"search: Retrieved top {len(indices)} indices.")

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
        log_error(f"search: Import error: {imp_err}")
        raise ImportError(f"search failed due to import issue: {imp_err}") from imp_err
    except sqlite3.Error as db_err:
        log_error(f"search: Database error: {db_err}")
        return []
    except Exception as err:
        log_error(f"search: Unexpected error: {err}")
        raise RuntimeError(f"search failed: {err}") from err
    finally:
        log_debug("search: Execution completed.")
