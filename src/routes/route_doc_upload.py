"""
File Upload API Endpoint

This module provides FastAPI routes for handling file uploads,
including file type validation and secure storage.
"""

import logging
import os
import sys
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

# Add root dir and handle potential import errors
try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info  # Removed unused log_debug
    from src.helpers import get_settings, Settings
    from src.controllers import get_clean_file_name

except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

upload_route = APIRouter()

UPLOAD_DIR = get_settings().DOC_LOCATION_SAVE
os.makedirs(UPLOAD_DIR, exist_ok=True)


@upload_route.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    app_settings: Settings = Depends(get_settings)
):
    """
    Endpoint to upload and securely store a file.

    Args:
        file (UploadFile): The file being uploaded.
        app_settings (Settings): App configuration settings.

    Returns:
        JSONResponse: Result of upload process, success or error.
    """
    try:
        # Generate a clean and sanitized file name
        unique_filename = get_clean_file_name(file.filename)
        file_location = os.path.join(UPLOAD_DIR, unique_filename)

        # Extract file extension
        file_extension = os.path.splitext(unique_filename)[1].lower()

        # Check if the file type is allowed
        if file_extension not in app_settings.FILE_ALLOWED_TYPES:
            return JSONResponse(
                content="The file type is not supported.",
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )

        # Save the file to disk
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        log_info(
            f"File uploaded and saved as '{unique_filename}' at '{file_location}'"
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully.",
                "filename": unique_filename,
                "saved_to": file_location
            }
        )

    except Exception as upload_exception:
        log_error(f"Failed to upload file '{file.filename}': {upload_exception}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed."
        ) from upload_exception  # fixed raise-missing-from
