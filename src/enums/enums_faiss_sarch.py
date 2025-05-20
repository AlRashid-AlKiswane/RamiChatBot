"""
Enums for FAISS search log messages and raised exceptions.
"""

from enum import Enum


class FaissSearchLogMessages(Enum):
    """Enum for FAISS search log and error messages."""

    INFO_START_BUILD = "[FAISS_BUILD] Starting to build FAISS index."
    INFO_INDEX_SUCCESS = "[FAISS_BUILD] FAISS index successfully created."

    ERR_IMPORT_FAILURE = "[FAISS_IMPORT_ERROR] Failed to set up FAISS module: {}"
    ERR_BUILD_FAILED = "[FAISS_BUILD_ERROR] Exception occurred while building FAISS index: {}"

    RAISE_INVALID_EMBEDDINGS = "Invalid embeddings: expected a 2D NumPy array."
    RAISE_INDEX_BUILD_FAILED = "Failed to build FAISS index: {}"
