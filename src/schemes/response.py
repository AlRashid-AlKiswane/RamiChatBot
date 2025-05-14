"""
Response generation schema module.

This module defines Pydantic models for handling and validating
query inputs for response generation.
"""

from pydantic import BaseModel, Field, validator

class Generate(BaseModel):
    """Model for validating and processing generation queries.

    Attributes:
        query: The user input query with length constraints (1-2048 characters)
    """
    query: str = Field(..., min_length=1, max_length=2048, description="The user input query.")

    @validator('query')
    def strip_and_validate_query(self, value: str) -> str:
        """Validate and clean the query string.

        Args:
            value: The raw query string

        Returns:
            The stripped and validated query string

        Raises:
            ValueError: If the query is empty or whitespace only
        """
        value = value.strip()
        if not value:
            raise ValueError("Query must not be empty or whitespace only.")
        return value
