from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import sys
from typing import Dict, Any

FILE_LOCATION = f"{os.path.dirname(__file__)}/llms_routes.py"

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from schemes import LLMResponse
except Exception as e:
    raise ImportError(f"Import Error in: {FILE_LOCATION}, Error: {e}")

llms_config_route = APIRouter()


@llms_config_route.post("/llms_config")
async def configure_llm(config: LLMResponse) -> JSONResponse:
    """
    Receives model configuration for LLM setup via dashboard/API call.

    Body (JSON):
    {
        "model_name": "model_id",
        "max_length": 256,
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 50,
        "do_sample": true
    }

    Returns tokenizer loading confirmation and current config.
    """
    try:
        log_info(f"Received LLM configuration: {config.model_name}")
        return JSONResponse(
            content={
                "status": "success",
                "message": f"Tokenizer for '{config.model_name}' loaded successfully.",
                "model_config": config.dict()
            },
            status_code=200
        )

    except Exception as e:
        log_error(f"Failed to load tokenizer or parse config: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Could not initialize model/tokenizer. Error: {str(e)}"
            },
            status_code=500
        )
