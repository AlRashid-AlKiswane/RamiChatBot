"""
Live RAG (Retrieval-Augmented Generation) configuration schemas.

This module defines Pydantic models for live RAG operations,
including query handling and retrieval parameters.
"""

from pydantic import BaseModel

class LiveRAG(BaseModel):
    """Configuration model for Live RAG operations.

    Attributes:
        query: The input query/question for RAG system
        top_k: Number of top documents to retrieve (default: 1)
    """
    query: str
    top_k: int = 1
