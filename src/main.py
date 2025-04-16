import os
import sys
from fastapi import FastAPI

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from api import hello_routes, upload_route, to_chunks_route, llms_config_route
    from utils import load_last_yaml
    from llm import HuggingFcaeModel
except Exception as e:
    msg = f"Import Error in: {os.path.dirname(__file__)}, Error: {e}"
    raise ImportError(msg)

LLM_CONFIG = load_last_yaml( file_path=None)

PROMPT = 
model = 
# Initialize FastAPI app
app = FastAPI()
generateror = HuggingFcaeModel()
generateror.init_llm(**LLM_CONFIG)
response = generateror.generate_response(prompt=prompt)
# Include routers
app.include_router(hello_routes, prefix="/api", tags=["Hello"])
app.include_router(upload_route, prefix="/api", tags=["Upload File"])
app.include_router(to_chunks_route, prefix="/api", tags=["Documents to Chunks"])
app.include_router(llms_config_route, prefix="/api", tags=["LLMs Cofnigs"])




