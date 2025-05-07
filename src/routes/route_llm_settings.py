from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from typing import Optional
import os
import sys

FILE_LOCATION = os.path.join(os.path.dirname(__file__), "llms.py")

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
    from llm import HuggingFaceLLMs, CPPLlaMa
    from schemes import LLMResponse, LlamaCPP
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {FILE_LOCATION}: {e}")

llm_settings_route = APIRouter()

@llm_settings_route.post("/application")
async def apply_model_settings(
    request: Request,
    load_type: Optional[str] = "HF",
    body: Optional[LLMResponse] = Body(None),
    cpp_body: Optional[LlamaCPP] = Body(None)
):
    """
    Initialize and apply configuration to either HuggingFace or LlamaCPP model.
    """
    try:
        if load_type == "HF":
            if not body:
                return JSONResponse(
                    content={"error": "Missing HuggingFace model parameters."},
                    status_code=HTTP_400_BAD_REQUEST
                )

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

            hf_llm = HuggingFaceLLMs()
            hf_llm.initilize_llm(model_name=body.model_name, **model_config)
            request.app.state.llm = hf_llm

            log_info(f"[APPLICATION] HuggingFace model '{body.model_name}' initialized successfully.")
            return JSONResponse(
                content={"message": f"HuggingFace model '{body.model_name}' initialized successfully."},
                status_code=HTTP_200_OK
            )

        elif load_type == "lCPP":
            if not cpp_body:
                return JSONResponse(
                    content={"error": "Missing LlamaCPP model parameters."},
                    status_code=HTTP_400_BAD_REQUEST
                )

            model_config = {
                "n_ctx": cpp_body.n_ctx,
                "n_threads": cpp_body.n_threads,
                "seed": cpp_body.seed,
                "n_gpus": cpp_body.n_gpus,
                "verbose": cpp_body.verbose,
                "max_tokens": cpp_body.max_tokens,
                "temperature": cpp_body.temperature,
                "top_p": cpp_body.top_p,
                "echo": cpp_body.echo,
                "stop": cpp_body.stop,
            }

            cpp_llm = CPPLlaMa()
            cpp_llm.initilize_llm(repo_id=cpp_body.repo_id, filename=cpp_body.filename, **model_config)
            request.app.state.llm = cpp_llm

            log_info(f"[APPLICATION] LlamaCPP model '{cpp_body.repo_id}' initialized successfully.")
            return JSONResponse(
                content={"message": f"LlamaCPP model '{cpp_body.repo_id}' initialized successfully."},
                status_code=HTTP_200_OK
            )

        else:
            return JSONResponse(
                content={"error": "Invalid load_type. Choose 'HF' or 'lCPP'."},
                status_code=HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        log_error(f"[APPLICATION ERROR] load_type={load_type} | Exception: {e}")
        return JSONResponse(
            content={"error": f"Failed to initialize model: {str(e)}"},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )
