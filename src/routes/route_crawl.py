"""
Website Crawler API Endpoint

This module provides FastAPI routes for crawling websites, tracking memory usage,
and saving crawled content to text files.
"""

import logging
import os
import sys
import tracemalloc
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

# Setup import path and logging
try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from logs import log_error, log_info  # log_debug removed (unused)
    from controllers import WebsiteCrawler
    from schemes import CrawlRequest

except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

crawler_route = APIRouter()


@crawler_route.post("/crawl")
async def crawl_website(request: CrawlRequest):
    """
    Endpoint to crawl a website starting from the given URL and save the result to text files.

    Args:
        request (CrawlRequest): Contains the start URL and max number of pages to crawl.

    Returns:
        JSONResponse: File path of saved results or HTTP error.
    """
    tracemalloc.start()
    try:
        log_info(f"Received crawl request for {request.start_url}")
        crawler = WebsiteCrawler(
            start_url=str(request.start_url),
            max_pages=request.max_pages,
        )

        visited = crawler.crawl()
        if not visited:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No pages were visited during crawl",
            )

        saved_file = crawler.save_to_text_files(visited)

        current, peak = tracemalloc.get_traced_memory()
        log_info(
            f"Memory usage during crawl: Current = {current / 1024:.2f} KB, "
            f"Peak = {peak / 1024:.2f} KB"
        )
        tracemalloc.stop()

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"file_path": saved_file},
        )

    except HTTPException as http_err:
        log_error(f"HTTP error: {http_err.detail}")
        raise http_err

    except Exception as exc:
        log_error(
            "Internal Server Error during crawl:\n"
            f"{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error occurred during crawling",
        ) from exc  # added `from exc`
