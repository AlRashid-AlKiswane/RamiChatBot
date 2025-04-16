import os
import sys
from fastapi import FastAPI

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from api import hello_routes, upload_route, to_chunks_route
except Exception as e:
    msg = f"Import Error in: {os.path.dirname(__file__)}, Error: {e}"
    raise ImportError(msg)

# Initialize FastAPI app
app = FastAPI()

# Include routers
app.include_router(hello_routes, prefix="/api", tags=["Hello"])
app.include_router(upload_route, prefix="/api", tags=["Upload File"])
app.include_router(to_chunks_route, prefix="/api", tags=["Documents to Chunks"])

