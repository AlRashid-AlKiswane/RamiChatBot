"""
embedding_query module.

Provides structured logging messages for embedding user queries into vector
representations. This module centralizes log and exception messages used
throughout the embedding process to ensure consistent and clear communication
of states, warnings, errors, and exceptions.

The messages cover informational events, warnings about deprecated features or
performance issues, errors encountered during the embedding process, and
exception messages used when raising exceptions.

Enums:
    EmbeddingQueryLogMessages: Contains categorized log messages for embedding
                               user queries, facilitating easier maintenance
                               and consistent logging.
"""

from enum import Enum


class EmbeddingQueryLogMessages(Enum):
    """
    Enumeration of log messages used in the embedding_query module.

    This enum categorizes messages by their severity and purpose, including:

    - Informational messages indicating normal progress of the embedding process.
    - Warning messages highlighting deprecated features or performance issues.
    - Error messages intended for logging runtime and data-related errors.
    - Exception raise messages intended for use when raising exceptions.

    Attributes:
        INFO_STARTING_EMBED (str): Log when embedding starts for a specific query.
        INFO_EMBED_SUCCESS (str): Log when embedding completes successfully.
        INFO_EMBED_COMPLETED (str): Log when embedding operation is fully done.
        WARN_DEPRECATED_FEATURE (str): Warn about usage of deprecated features.
        WARN_SLOW_EMBEDDING (str): Warn about embedding operation taking too long.
        ERR_IMPORT_FAILURE (str): Log import failures in embedding module.
        ERR_EMBEDDING_RUNTIME (str): Log runtime errors during embedding.
        ERR_VALUE_ERROR (str): Log value errors encountered.
        ERR_JSON_DECODE (str): Log JSON decoding errors.
        ERR_TYPE_ERROR (str): Log type errors encountered.
        ERR_KEY_ERROR (str): Log key errors encountered.
        ERR_UNKNOWN (str): Log unknown/unexpected errors.
        RAISE_IMPORT_ERROR (str): Message for raising import errors.
        RAISE_VALUE_ERROR (str): Message for raising value errors.
        RAISE_RUNTIME_ERROR (str): Message for raising runtime errors.
        RAISE_UNKNOWN_ERROR (str): Message for raising unknown errors.
    """

    # Informational messages
    INFO_STARTING_EMBED = "Starting embedding for query: '{}'"
    INFO_EMBED_SUCCESS = "Embedding successful for query."
    INFO_EMBED_COMPLETED = "Embedding operation completed."

    # Warning messages
    WARN_DEPRECATED_FEATURE = "Deprecated feature used in embedder: '{}'"
    WARN_SLOW_EMBEDDING = "Embedding operation took longer than expected: {} seconds."

    # Error messages (logged errors)
    ERR_IMPORT_FAILURE = "Import error in embedding_query module: {}"
    ERR_EMBEDDING_RUNTIME = "Runtime error during embedding: {}"
    ERR_VALUE_ERROR = "Value error encountered: {}"
    ERR_JSON_DECODE = "JSON decode error in embedding data: {}"
    ERR_TYPE_ERROR = "Type error encountered: {}"
    ERR_KEY_ERROR = "Key error encountered: {}"
    ERR_UNKNOWN = "Unknown error occurred: {}"

    # Exception raise messages (used when raising exceptions)
    RAISE_IMPORT_ERROR = "Failed to import necessary modules for embedding_query: {}"
    RAISE_VALUE_ERROR = "Error embedding query due to invalid value: {}"
    RAISE_RUNTIME_ERROR = "Runtime error while embedding query: {}"
    RAISE_UNKNOWN_ERROR = "An unexpected error occurred: {}"
