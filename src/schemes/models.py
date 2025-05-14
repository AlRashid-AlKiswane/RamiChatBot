"""
Database model schemas for chunk processing and query responses.

This module defines Pydantic models for:
- Chunk processing requests
- Text chunks with metadata
- Embedding storage
- Query responses
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel

class ChunkRequest(BaseModel):
    """Request model for chunk processing operations.

    Attributes:
        file_path: Optional path to file for chunking
        do_reset: Flag to reset processing (0 = no reset, 1 = reset)
    """
    file_path: Optional[str] = None
    do_reset: int = 0

class Chunk(BaseModel):
    """Model representing a text chunk with metadata.

    Attributes:
        chunks: The text content of the chunk
        metadata: Dictionary of associated metadata
    """
    chunks: str
    metadata: Dict[str, Any]

class Embedding(BaseModel):
    """Model for storing embedding vectors.

    Attributes:
        chunk_id: Reference ID to the source chunk
        embedding: Binary representation of the embedding vector
    """
    chunk_id: int
    embedding: bytes

class QueryResponse(BaseModel):
    """Model for storing query responses.

    Attributes:
        query: The original query text
        response: The generated response text
    """
    query: str
    response: str
