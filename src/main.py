import os
import sys
from fastapi import FastAPI

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from api import (hello_routes, 
                     upload_route, 
                     to_chunks_route, 
                     llms_config_route, 
                     generate_routes)
except Exception as e:
    msg = f"Import Error in: {os.path.dirname(__file__)}, Error: {e}"
    raise ImportError(msg)

# Initialize FastAPI app
app = FastAPI()

app.include_router(hello_routes, prefix="/api", tags=["Hello"])
app.include_router(upload_route, prefix="/api", tags=["Upload File"])
app.include_router(to_chunks_route, prefix="/api", tags=["Documents to Chunks"])
app.include_router(llms_config_route, prefix="/api", tags=["LLMs Cofnigs"])
app.include_router(generate_routes, prefix="/api", tags=["Chat Response"])





