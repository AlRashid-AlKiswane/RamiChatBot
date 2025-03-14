import os
import sys
from fastapi import FastAPI, APIRouter, Depends

# Add the project's root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)

from utils.helpers import get_settings, Settings
from enums.api.hello import HelloProcessing

# Define the router correctly
hello_router = APIRouter()

@hello_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
        "message": HelloProcessing.MESSAGE.value
    }
