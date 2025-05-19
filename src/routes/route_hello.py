"""
Hello World API Endpoint

This module provides a simple FastAPI endpoint that returns basic application
information including the app name, version, and a greeting message.
"""

import logging
import os
import sys
from fastapi import APIRouter, Depends
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

    from src.logs import log_info
    from src.helpers import get_settings, Settings
    from src.enums import HelloResponse

except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

# Define the router
hello_routes = APIRouter()

@hello_routes.get("/hello")
async def say_hello(app_settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Return basic application information and greeting.
    
    Args:
        app_settings: Application settings (dependency injection)
        
    Returns:
        JSONResponse: Contains app name, version, and greeting message
    """
    try:
        name_app = app_settings.APP_NAME
        version_app = app_settings.APP_VERSION

        log_info(f"App info retrieved: {name_app} {version_app}")
        return JSONResponse(
            content={
                "App Name": name_app,
                "Version": version_app,
                "Message": HelloResponse.APIRUN.value
            }
        )

    except Exception:  # pylint: disable=broad-except
        return JSONResponse(
            content={
                "App Name": "Unknown",
                "Version": "Unknown",
                "Message": HelloResponse.APIBREAK.value
            },
            status_code=500
        )
