"""
faiss_search module for RAG: building FAISS indices from embeddings.
"""

import faiss
import numpy as np

from src.logs import log_error, log_info


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
