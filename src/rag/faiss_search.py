"""
faiss_search module for RAG: provides functionality to build a FAISS index
from a set of vector embeddings for efficient similarity search.
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

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.enums import FaissSearchLogMessages

except (FileNotFoundError, OSError) as e:
    logging.error("Fatal error setting up project directory: %s", str(e))
    logging.error(traceback.format_exc())
    sys.exit(1)


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """
    Build a FAISS IndexFlatL2 index from the provided vector embeddings.

    Args:
        embeddings (np.ndarray): A 2D numpy array of shape (n_vectors, dim),
                                 where n_vectors is the number of vectors
                                 and dim is the dimensionality.

    Returns:
        faiss.IndexFlatL2: A FAISS index with the input vectors.

    Raises:
        ValueError: If the embeddings array is not valid or indexing fails.
    """
    try:
        log_info(FaissSearchLogMessages.INFO_START_BUILD.value)

        if not isinstance(embeddings, np.ndarray) or len(embeddings.shape) != 2:
            raise ValueError(FaissSearchLogMessages.RAISE_INVALID_EMBEDDINGS.value)

        dim = embeddings.shape[1]  # Correctly extract the dimensionality
        index = faiss.IndexFlatL2(dim)
        n_vectors = embeddings.shape[0]  # Extract the number of vectors
        index.add(embeddings, n_vectors)  # Pass both x and n arguments

        log_info(FaissSearchLogMessages.INFO_INDEX_SUCCESS.value)
        return index

    except Exception as err:
        log_error(FaissSearchLogMessages.ERR_BUILD_FAILED.value.format(str(err)))
        raise ValueError(FaissSearchLogMessages.RAISE_INDEX_BUILD_FAILED.value.format(
            str(err)
            )) from err
