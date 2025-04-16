import os
import sys
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from utils import load_last_yaml
    from llm import HuggingFcaeModel
    from prompt import PromptRami
    from schemes import Generate
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

# Load model config only once at app startup
try:
    LLM_CONFIG = load_last_yaml()
    if not LLM_CONFIG:
        raise ValueError("No valid config found for LLM.")
    log_info("[LLM] Loaded model config successfully.")
except Exception as e:
    log_error(f"[LLM INIT ERROR] {e}")
    raise e

# Initialize and cache the model instance
try:
    model = HuggingFcaeModel()
    model.init_llm(**LLM_CONFIG)
    log_info("[LLM] Model initialized successfully.")
except Exception as e:
    log_error(f"[LLM INIT ERROR] {e}")
    raise RuntimeError("Failed to initialize LLM") from e

RETRIEVAL_CONTEXT = "..."  # You can hook this into your vector store / RAG retrieval

generate_routes = APIRouter()


@generate_routes.post("/chat", response_class=JSONResponse)
async def generate_response(body: Generate):
    """
    Generate response from LLM based on user query and retrieved context.
    """
    try:
        query = body.query
        prompt_template = PromptRami()
        final_prompt = prompt_template.prompt.format(
            retrieved_context=RETRIEVAL_CONTEXT,
            user_message=query
        )

        log_debug(f"[PROMPT] Final prompt:\n{final_prompt}")
        response_text = model.generate_response(prompt=final_prompt)

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status": "success",
                "response": response_text
            }
        )

    except Exception as e:
        log_error(f"[LLM GENERATION ERROR] {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Failed to generate response"
            }
        )
