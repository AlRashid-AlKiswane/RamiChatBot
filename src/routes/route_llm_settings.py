"""
LLM Model Configuration API Endpoint

This module provides FastAPI routes for initializing and configuring
different types of language models (HuggingFace, Cohere, OpenAI, Google, DeepSeek).
"""

import logging
import os
import sys
from typing import Optional
from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.llm import HuggingFaceLLM, CohereLLM, OpenAILLM, GoogleLLM, DeepSeekLLM
    from src.schemes import LLMResponse

except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


llm_settings_route = APIRouter()


@llm_settings_route.post("/application")
@llm_settings_route.post("/application")
async def apply_model_settings(
    request: Request,
    load_type: Optional[str] = "HF",
    body: Optional[LLMResponse] = Body(None),
):
    """
    Initialize and configure language models.

    Args:
        request: FastAPI Request object
        load_type: Model type to initialize ('HF', 'Cohere', 'OpenAI', 'Google', 'DeepSeek')
        body: Model parameters

    Returns:
        JSONResponse with success or error message and status code
    """
    if body is None:
        return JSONResponse(
            content={"error": "Missing model parameters."},
            status_code=HTTP_400_BAD_REQUEST,
        )

    common_params = {
        "model_name": body.model_name,
        "temperature": getattr(body, "temperature", None),
        "max_new_tokens": getattr(body, "max_new_tokens", None),
        "top_p": getattr(body, "top_p", None),
        "top_k": getattr(body, "top_k", None),
    }

    try:
        # Define a dispatch dict for cleaner logic
        def init_hf():
            hf_params = {
                "max_new_tokens": common_params["max_new_tokens"],
                "temperature": common_params["temperature"],
                "top_p": common_params["top_p"],
                "top_k": common_params["top_k"],
                "trust_remote_code": body.trust_remote_code,
                "do_sample": body.do_sample,
                "quantization": body.quantization,
                "quantization_type": body.quantization_type,
            }
            llm = HuggingFaceLLM()
            llm.initialize_llm(model_name=common_params["model_name"], **hf_params)
            return llm

        def init_cohere():
            cohere_params = {
                "temperature": common_params["temperature"],
                "max_new_tokens": common_params["max_new_tokens"],
                "top_k": common_params["top_k"],
                "top_p": common_params["top_p"],
            }
            llm = CohereLLM()
            llm.initialize_llm(model_name=common_params["model_name"], **cohere_params)
            return llm

        def init_openai():
            openai_params = {
                "temperature": common_params["temperature"],
                "max_new_tokens": common_params["max_new_tokens"],
                "top_p": common_params["top_p"],
            }
            llm = OpenAILLM()
            llm.initialize_llm(model_name=common_params["model_name"], **openai_params)
            return llm

        def init_google():
            google_params = {
                "temperature": common_params["temperature"],
                "max_new_tokens": common_params["max_new_tokens"],
                "top_p": common_params["top_p"],
            }
            llm = GoogleLLM()
            llm.initialize_llm(model_name=common_params["model_name"], **google_params)
            return llm

        def init_deepseek():
            deepseek_params = {
                "temperature": common_params["temperature"],
                "max_new_tokens": common_params["max_new_tokens"],
                "top_p": common_params["top_p"],
            }
            llm = DeepSeekLLM()
            llm.initialize_llm(model_name=common_params["model_name"], **deepseek_params)
            return llm

        dispatch = {
            "HF": init_hf,
            "Cohere": init_cohere,
            "OpenAI": init_openai,
            "Google": init_google,
            "DeepSeek": init_deepseek,
        }

        if load_type not in dispatch:
            return JSONResponse(
                content={
                    ("""error": "Invalid load_type.
                      Choose among 'HF', 'Cohere', 'OpenAI', 'Google', 'DeepSeek'.""")
                },
                status_code=HTTP_400_BAD_REQUEST,
            )

        llm_instance = dispatch[load_type]()
        request.app.state.llm = llm_instance

        log_info(f"[APPLICATION] {load_type} model '{common_params['model_name']}' initialized.")
        return JSONResponse(
            content={"message": f"{load_type} model '{common_params['model_name']}' initialized."},
            status_code=HTTP_200_OK,
        )

    except ValueError as e:
        log_error(f"[APPLICATION ERROR] load_type={load_type} | ValueError: {e}")
        return JSONResponse(
            content={"error": f"Invalid input: {str(e)}"},
            status_code=HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as e:
        log_error(f"[APPLICATION ERROR] load_type={load_type} | RuntimeError: {e}")
        return JSONResponse(
            content={"error": f"Runtime error occurred: {str(e)}"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except (TypeError, KeyError, AttributeError) as e:
        log_error(f"[APPLICATION ERROR] load_type={load_type} | Specific Exception: {e}")
        return JSONResponse(
            content={"error": f"A specific error occurred: {str(e)}"},
            status_code=HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        log_error(f"[APPLICATION ERROR] load_type={load_type} | Unexpected Exception: {e}")
        raise
