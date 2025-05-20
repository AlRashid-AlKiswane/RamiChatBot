"""
database_retrieval module.

Provides functionality for loading embeddings and metadata from a database,
with structured logging and error handling using the DBRetrievalMessages enum.

The module logs key events such as the start and successful completion of
data loading, as well as various error conditions including SQLite errors
and data processing errors.

Enums:
    DBRetrievalMessages: Contains all log and error message templates used
                         throughout the database retrieval process.

Typical usage:
    - Start loading embeddings and metadata from the database.
    - Log progress and handle any SQLite or data-related errors gracefully.
    - Confirm completion with detailed logging.
"""

from enum import Enum

class DBRetrievalMessages(Enum):
    """Enum class for log and error messages in database_retrieval module."""

    LOAD_START = "Starting to load embeddings and metadata from the database."
    LOAD_SUCCESS = "Successfully loaded {} embeddings and {} metadata entries."
    NO_EMBEDDINGS_FOUND = "No embeddings found in the database."
    SQLITE_ERROR = "SQLite error occurred: {}"
    DATA_ERROR = "Data processing error occurred: {}"
    FUNCTION_COMPLETED = ("database_retrieval.load_embeddings_and_metadata:"
                           "Function execution completed.")
