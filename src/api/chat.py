import os
import sys
import tracemalloc
import traceback
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
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
tracemalloc.start()

@generate_routes.post("/chat", response_class=JSONResponse)
async def generate_response(request: Request, body: Generate, user_id: str, prompt_template_name: str = "llama"):
    """
    Generate response from LLM based on user query and retrieved context.
    """
    try:
        query = body.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
        chat_manager = getattr(request.app, "chat_manager", None)
        model = getattr(request.app, "model", None)
        conn = getattr(request.app, "conn", None)
        context = getattr(request.app, "RETRIEVAL_CONTEXT", "")

        if not all([chat_manager, model, conn]):
            raise HTTPException(status_code=500, detail="Application is not properly initialized.")

        # Build the prompt
        formatted_prompt = PromptBuilder.build_prompt(
            history=chat_manager.get_chat_history(),
            context=context,
            user_message=query
        )
        log_info(f"[LLM GENERATION] Generating response for query: {query}")

        # Generate model response
        response = model.generate_response(prompt=formatted_prompt)
        single_response = extract_assistant_response(text=response)

        # Store in DB
        insert_query_response(
            conn=conn,
            query=formatted_prompt,
            response=response
        )        

        # Update memory
        chat_manager.add_user_message(user_id, query)
        chat_manager.add_ai_message(user_id, single_response)

        # Log memory usage
        current, peak = tracemalloc.get_traced_memory()
        log_debug(f"Current memory usage: {current / 1024:.2f} KB")
        log_debug(f"Peak memory usage: {peak / 1024:.2f} KB")

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "status": "success",
                "response": single_response
            }
        )

    except HTTPException as http_exc:
        log_error(f"[LLM GENERATION HTTP ERROR] {http_exc.detail}")
        raise http_exc

    except Exception as e:
        log_error(f"[LLM GENERATION ERROR] {traceback.format_exc()}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Failed to generate response. Please try again later."
            }
        )
    finally:
        log_info(f"[LLM GENERATION] Finished processing request.")
