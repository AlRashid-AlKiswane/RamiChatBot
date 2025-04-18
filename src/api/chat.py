import os
import sys
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from prompt import PromptRamiLlaMA, PromptRamiJAIS
    from schemes import Generate
    from Database import insert_query_response
    from enums import LLMNames
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")


RETRIEVAL_CONTEXT = "Time work  5 Day in week s, m , t, w, "  # You can hook this into your vector store / RAG retrieval

generate_routes = APIRouter()


@generate_routes.post("/chat", response_class=JSONResponse)
async def generate_response(request: Request, body: Generate, prompt_template_name: str = "llama"):
    """
    Generate response from LLM based on user query and retrieved context.
    """
    try:
        query = body.query

        if prompt_template_name.lower() == "llama":
            prompt_template = PromptRamiLlaMA()
            final_prompt = prompt_template.prompt.format(
                retrieved_context=RETRIEVAL_CONTEXT,
                user_message=query
            )
            log_debug(f"[PROMPT] Final prompt:\n{final_prompt}, Note: Llama model is used")
            response_text = request.app.model.generate_response(prompt=final_prompt)

        elif prompt_template_name.lower() == "jais":
            prompt_template = PromptRamiJAIS()
            final_prompt = prompt_template.prompt.format(
                retrieved_context=RETRIEVAL_CONTEXT,
                user_message=query
            )
            log_debug(f"[PROMPT] Final prompt:\n{final_prompt}, Note: Jais model is used")
            response_text = request.app.model.generate_response(prompt=final_prompt)

        else:
            raise ValueError("Unsupported model name")

        insert_query_response(
            conn=request.app.conn,
            query=query,
            response=response_text
        )        
        log_info(f"[LLM RESPONSE] {response_text}")

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
    finally:
        log_info(f"[LLM GENERATION] Finished processing request.")