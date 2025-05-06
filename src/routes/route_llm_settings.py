# Refactored and optimized FastAPI route with full error handling, validation, and logging.
# Also integrates with the new `HuggingFaceLLMs` LLM class instead of HuggingFaceLLMs.

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
import os
import sys
from typing import Optional

FILE_LOCATION = os.path.join(os.path.dirname(__file__), "llms.py")

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
    from config import Settings, get_settings
    from enums import LLMsStatus
    from llm import HuggingFaceLLMs  # renamed creative class
    from schemes import LLMResponse
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {FILE_LOCATION}: {e}")

llm_settings_route = APIRouter()

@llm_settings_route.post("/application")
async def apply_model_settings(request: Request, body: LLMResponse):
    """
    Receive model application parameters, initialize model, and store in app state.
    """
    model_name = body.model_name

    model_config = {
        "max_new_tokens": body.max_new_tokens,
        "temperature": body.temperature,
        "top_p": body.top_p,
        "top_k": body.top_k,
        "trust_remote_code": body.trust_remote_code,
        "do_sample": body.do_sample,
        "quantization": body.quantization,
        "quantization_type": body.quantization_type,
    }

    try:
        llm_instance = HuggingFaceLLMs()
        llm_instance.initilize_llm(model_name=model_name,
                                   **model_config)
        request.app.state.llm = llm_instance
        log_info(f"[APPLICATION] Model '{body.model_name}' initialized with provided configuration.")
        return JSONResponse(
            content={"message": "Application parameters applied successfully."},
            status_code=HTTP_200_OK
        )

    except Exception as e:
        log_error(f"[APPLICATION ERROR] Failed to initialize model: {e}")
        return JSONResponse(
            content={"error": f"Failed to initialize model: {str(e)}"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )
