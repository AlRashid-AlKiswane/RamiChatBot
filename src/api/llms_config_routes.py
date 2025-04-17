from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import sys
import yaml
import re
from typing import Any

FILE_LOCATION = os.path.join(os.path.dirname(__file__), "llms_routes.py")

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
    from config import Settings, get_settings
    from enums import LLMsConfigStatus
    from schemes import LLMResponse
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {FILE_LOCATION}: {e}")

# Load settings and ensure config directory exists
APP_SETTINGS: Settings = get_settings()
CONFIG_DIR = APP_SETTINGS.CONFIG_DIR
os.makedirs(CONFIG_DIR, exist_ok=True)

llms_config_route = APIRouter()

@llms_config_route.post("/llms_config")
async def configure_llm(config: LLMResponse,
                        request: Request) -> JSONResponse:
    """
    Saves model configuration to a YAML file using model name as the filename,
    and initializes the model on-the-fly if not already loaded.
    """
    try:
        log_info(f"[LLM CONFIG] Saving config for model: {config.model_name}")

        safe_model_name = re.sub(r'[^a-zA-Z0-9]', '_', config.model_name)
        config_path = os.path.join(CONFIG_DIR, f"{safe_model_name}_config.yaml")

        # Write config
        with open(config_path, "w") as f:
            yaml.safe_dump(config.dict(), f, default_flow_style=False)
        
        # Set config to app instance directly
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
        error_message = f"[LLM CONFIG ERROR] {e}"
        log_error(error_message)

        return JSONResponse(
            content={
                "status": LLMsConfigStatus.ERROR.name,
                "message": LLMsConfigStatus.ERROR.value,
                "detail": str(e)
            },
            status_code=500
        )

