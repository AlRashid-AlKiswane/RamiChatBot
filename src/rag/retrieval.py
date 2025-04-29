import os
import sys
from typing import List, Dict, Any
import numpy as np
import sqlite3

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from .__faissSarch import build_faiss_index
    from .embed_query import embed_query
    from .__pull_from_databse import load_embeddings_and_metadata
    from embedding import EmbeddingModel
    from logs import log_debug, log_error, log_info

except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")


def search(
    query: str,
    embedder: EmbeddingModel,
    conn: sqlite3.Connection,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for the most relevant page_contents and their ids based on the query.

    Args:
        query (str): The input query string.
        embedder (EmbeddingModel): The embedding model instance.
        conn (sqlite3.Connection): The database connection instance.
        top_k (int): Number of top similar entries to return.

    Returns:
        List[Dict[str, Any]]: List of dictionaries with 'id' and 'page_content'.
    """
    try:
        log_info(f"[SEARCH] Starting search for query: {query[:30]}...")


        # Step 2: Load embeddings and metadata
        ids, embeddings_array, metadata = load_embeddings_and_metadata(conn)
        if len(ids) == 0:
            log_error("[SEARCH] No embeddings found in the database.")
            return []

        # Step 3: Build the FAISS index
        index = build_faiss_index(embeddings_array)

        # Step 4: Embed the query
        query_vector = embed_query(query, embedder, convert_to_tensor=False, normalize_embeddings=False)
        if isinstance(query_vector, list):
            query_vector = np.array(query_vector).astype(np.float32)

        # Step 5: Perform the FAISS search
        distances, indices = index.search(np.expand_dims(query_vector, axis=0), top_k)

        log_info(f"[SEARCH] Found {len(indices[0])} results for the query.")

        # Step 6: Fetch page_content and id for matching ids
        cursor = conn.cursor()

        result_entries = []
        for idx in indices[0]:
            if idx == -1:
                continue  # No match

            chunk_id = ids[idx]  # id from embeddings table (linked to chunks.id)

            # Fetch page_content and id from chunks table
            cursor.execute("SELECT id, page_contest FROM chunks WHERE id = ?", (chunk_id,))
            row = cursor.fetchone()
            if row:
                result_entries.append({
                    "id": row[0],
                    "page_content": row[1]
                })

        return result_entries

    except Exception as e:
        log_error(f"[SEARCH ERROR] {e}")
        raise RuntimeError(f"Search failed: {e}")

    finally:
        log_debug("[SEARCH] Search function executed.")
