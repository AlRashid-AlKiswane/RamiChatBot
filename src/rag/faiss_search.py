"""
faiss_search module for RAG: building FAISS indices from embeddings.
"""

import logging
import os
import sys
import traceback
import faiss
import numpy as np

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info

except (FileNotFoundError, OSError) as e:
    logging.error("Fatal error setting up project directory: %s", str(e))
    logging.error(traceback.format_exc())
    sys.exit(1)

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """
    Build and return a FAISS IndexFlatL2 from the provided embeddings.

    Args:
        embeddings: 2D numpy array of shape (n_vectors, dim).

    Returns:
        A FAISS IndexFlatL2 instance containing the embeddings.
    """
    try:
        log_info("[BUILD FAISS INDEX] Starting to build FAISS index.")
        n_vectors, dim = embeddings.shape
        index = faiss.IndexFlatL2(dim)
        index.add(n=n_vectors, x=embeddings)
        return index
    except Exception as err:
        log_error(f"[BUILD FAISS INDEX ERROR] {err}")
        raise
