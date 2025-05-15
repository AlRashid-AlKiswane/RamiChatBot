"""
Response generation schema module.

This module defines Pydantic models for handling and validating
query inputs for response generation.
"""

from pydantic import BaseModel, Field

class Generate(BaseModel):
    """Model for validating and processing generation queries.

    Attributes:
        query: The user input query with length constraints (1-2048 characters)
    """
    query: str = Field(..., min_length=1, max_length=2048, description="The user input query.")
