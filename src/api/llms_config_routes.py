from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import sys
import yaml
import re
from typing import Optional

FILE_LOCATION = os.path.join(os.path.dirname(__file__), "llms.py")

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
    from config import Settings, get_settings
    from enums import LLMsConfigStatus
    from schemes import LLMResponse, LlamaCPP
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {FILE_LOCATION}: {e}")

# Load settings and create config directory if needed
APP_SETTINGS: Settings = get_settings()
CONFIG_DIR = APP_SETTINGS.CONFIG_DIR
os.makedirs(CONFIG_DIR, exist_ok=True)

llms_config_route = APIRouter()

# Utility functions
def sanitize_model_name(model_name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '_', model_name)

def save_config(config: dict, filename: str) -> str:
    config_path = os.path.join(CONFIG_DIR, filename)
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    return config_path

# HuggingFace configuration route
@llms_config_route.post("/llms_config/huggingface")
async def configure_huggingface_model(
    request: Request,
    config: LLMResponse
) -> JSONResponse:
    try:
        log_info(f"[LLM CONFIG] Saving HuggingFace config for model: {config.model_name}")
        safe_name = sanitize_model_name(config.model_name)
        filename = f"{safe_name}_huggingface_config.yaml"
        config_path = save_config(config.dict(), filename)

        request.app.LLM_CONFIG = config.dict()

        return JSONResponse(
            content={
                "status": LLMsConfigStatus.SUCCESS.name,
                "message": LLMsConfigStatus.SUCCESS.value,
                "file": config_path
            },
            status_code=200
        )

    except Exception as e:
        log_error(f"[HUGGINGFACE CONFIG ERROR] {e}")
        return JSONResponse(
            content={
                "status": LLMsConfigStatus.ERROR.name,
                "message": LLMsConfigStatus.ERROR.value,
                "detail": str(e)
            },
            status_code=500
        )

# LLaMA.cpp configuration route
@llms_config_route.post("/llms_config/llama_cpp")
async def configure_llama_cpp_model(
    request: Request,
    config: LlamaCPP
) -> JSONResponse:
    try:
        log_info(f"[LLM CONFIG] Saving LLaMA.cpp config for model: {config.model_name}")
        safe_name = sanitize_model_name(config.model_name)
        filename = f"{safe_name}_llama_cpp_config.yaml"
        config_path = save_config(config.dict(), filename)

        request.app.LLM_CONFIG = config.dict()

        return JSONResponse(
            content={
                "status": LLMsConfigStatus.SUCCESS.name,
                "message": LLMsConfigStatus.SUCCESS.value,
                "file": config_path
            },
            status_code=200
        )

    except Exception as e:
        log_error(f"[LLAMA_CPP CONFIG ERROR] {e}")
        return JSONResponse(
            content={
                "status": LLMsConfigStatus.ERROR.name,
                "message": LLMsConfigStatus.ERROR.value,
                "detail": str(e)
            },
            status_code=500
        )
