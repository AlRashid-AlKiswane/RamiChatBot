"""
Log File Access API Endpoint

This module provides a FastAPI route for retrieving application log files.
It handles asynchronous file reading and proper error handling for log file access.
"""

import logging
import os
import sys
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
import aiofiles

# Setup import path and logging
try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error

except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

logers_router = APIRouter()

# Define the log file path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
LOG_FILE_PATH = f"{BASE_DIR}/log/app.log"

@logers_router.get("/logs", response_class=PlainTextResponse, status_code=HTTP_200_OK)
async def get_logs():
    """Retrieve and return the content of the application log file.
    
    Returns:
        PlainTextResponse: The content of the log file
        
    Raises:
        HTTPException: 
            404 if log file not found
            500 if error reading log file
    """
    # Verify that the log file exists
    if not os.path.exists(LOG_FILE_PATH):
        error_msg = "Log file not found."
        log_error(error_msg)
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=error_msg) from None

    try:
        # Use asynchronous file I/O to read the log file without blocking the event loop
        async with aiofiles.open(LOG_FILE_PATH, "r", encoding="utf-8") as log_file:
            logs = await log_file.read()
        log_debug("Successfully retrieved log file content.")
        return logs

    except Exception as e:
        error_msg = f"Error reading log file: {str(e)}"
        log_error(error_msg)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        ) from e
