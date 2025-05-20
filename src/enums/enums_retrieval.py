"""
Enums for retrieval module log and error messages.
"""

from enum import Enum


class RetrievalLogMessages(Enum):
    """Enum for log and raise messages in the retrieval module."""

    INFO_SEARCH_START = "[RETRIEVAL] Starting search for query: {}"
    INFO_INDICES_RETRIEVED = "[RETRIEVAL] Retrieved top {} indices."

    DEBUG_EXEC_COMPLETE = "[RETRIEVAL] Execution completed."

    ERR_IMPORT_FAILURE = "[RETRIEVAL IMPORT ERROR] Could not set up retrieval module: {}"
    ERR_NO_EMBEDDINGS = "[RETRIEVAL ERROR] No embeddings found in the database."
    ERR_IMPORT_ERROR = "[RETRIEVAL ERROR] Import error occurred: {}"
    ERR_DB_ERROR = "[RETRIEVAL ERROR] Database error occurred: {}"
    ERR_GENERAL_ERROR = "[RETRIEVAL ERROR] Unexpected exception: {}"

    RAISE_IMPORT_ERROR = "Import failure during retrieval: {}"
    RAISE_GENERAL_ERROR = "Search failed due to unexpected error: {}"
