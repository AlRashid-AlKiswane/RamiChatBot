import os
import sys
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from prompt import PromptBuilder
    from schemes import Generate
    from Database import insert_query_response
    from utils import extract_assistant_response
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")



generate_routes = APIRouter()
prompt_builder = PromptBuilder()



@generate_routes.post("/chat", response_class=JSONResponse)
async def generate_response(request: Request, body: Generate, prompt_template_name: str = "llama"):
    """
    Generate response from LLM based on user query and retrieved context.
    """
    try:
        query = body.query


        formatted_prompt = prompt = PromptBuilder.build_prompt(
            history=request.app.RETRIEVAL_CONTEXT,
            context=request.app.RETRIEVAL_CONTEXT,
            user_message=query
        )
        log_info(f"[LLM GENERATION] Generating response for query: {query}")

        
        response = request.app.model.generate_response(prompt=formatted_prompt)
        singel_response = extract_assistant_response(text=response)

        insert_query_response(
            conn=request.app.conn,
            query=formatted_prompt,
            response=response
        )        
        log_info(f"[LLM RESPONSE FINISHID]")

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status": "success",
                "response": singel_response
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