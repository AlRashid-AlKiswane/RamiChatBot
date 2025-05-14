"""
Web crawler configuration schemas.

This module defines Pydantic models for web crawling operations,
including URL validation and crawl limits.
"""

from pydantic import BaseModel, HttpUrl

class CrawlRequest(BaseModel):
    """Model for web crawling request parameters.

    Attributes:
        start_url: The starting URL for the crawl (must be valid HTTP/HTTPS URL)
        max_pages: Maximum number of pages to crawl (default: 10)
    """
    start_url: HttpUrl
    max_pages: int = 10
