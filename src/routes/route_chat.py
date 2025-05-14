import os
import sys
import tracemalloc
import traceback
import sqlite3 as sql3
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from prompt import PromptBuilder
    from schemes import Generate
    from dbs import (insert_query_response,
                     pull_from_table)
    from llm import HuggingFaceLLMs
    from embedding import EmbeddingModel
    from historys import ChatHistoryManager
    
    from utils import extract_llm_answer_from_full
    from rag import search

except ImportError as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

generate_routes = APIRouter()
prompt_builder = PromptBuilder()
tracemalloc.start()

def get_llm(request: Request):
    """Retrieve the LLM instance from the app state."""
    llm = request.app.state.llm
    if not llm:
        log_debug("LLM instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM service is not initialized. Please configure the LLM via the /llmsSettings endpoint."
        )
    return llm


def get_db_conn(request: Request):
    """Retrieve the relational database connection from the app state."""
    conn = request.app.state.conn
    if not conn:
        log_debug("Relational database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Relational database service is not available."
        )
    return conn

def get_embedd(request: Request):
    """Retrieve the embedding model instance from the app state."""
    embedding = request.app.state.embedding_model
    if not embedding:
        log_debug("Embedding model instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding model service is not available."
        )
    return embedding

def get_chat_history(request: Request):
    """Retrieve the get_chat_history model instance from the app state."""
    chat_history = request.app.state.chat_manager
    if not chat_history:
        log_debug("get_chat_history model instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get_chat_history model service is not available."
        )
    return chat_history

@generate_routes.post("/chat", response_class=JSONResponse)
async def generate_response(
    request: Request, 
    body: Generate, 
    user_id: str, 
    conn: sql3.Connection = Depends(get_db_conn),
    llm: HuggingFaceLLMs = Depends(get_llm),
    embedd: EmbeddingModel = Depends(get_embedd),
    chat_history: ChatHistoryManager = Depends(get_chat_history)
    ):
    """
    Generate response from LLM based on user query and retrieved context.
    """
    try:
        query = body.query.strip()
        if not query:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")
        
        # Extract application dependencies

        if not all([chat_history, llm, conn, embedd]):
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Application is not properly initialized.")

        cached_response = pull_from_table(conn=conn,
                                                   table_name="query_responses",
                                                   columns=[],  # Not used in cache mode
                                                   cach=(user_id, query)
        )
        if cached_response:
            # Use cached_response directly (it's a string)
                single_response = extract_llm_answer_from_full(cached_response)

                if single_response:
                    log_info(f"[CACHED HIT] Returning cached response for query: {query}")
                    return JSONResponse(
                        content={
                            "status": "success",
                            "response": single_response
                        },
                        status_code=HTTP_200_OK
                    )
        else:
            log_info(f"[CACHED MISS] No cached response found for query: {query}")
            # Retrieve context
            context = search(query=query, conn=conn, embedder=embedd, top_k=5)
            log_debug(f"Retrieveal: {context}")
            if not context:
                log_debug(f"[LLM GENERATION] No context found for query: {query}")
                context = "Empty"

            log_debug(f"[LLM GENERATION] Context retrieved: {context}")

            # Build the prompt
            formatted_prompt = prompt_builder.build_prompt(
                prompt_name="rami_issa",
                history=chat_history.get_chat_history(user_id),
                context=context,
                user_message=query)
            
            log_debug(f"[MEASSAGE HISTORY] {chat_history.get_chat_history(user_id)}")
            log_info(f"[LLM GENERATION] Generating response for query: {query}")

            # Generate model response
            raw_response = llm.generate_response(prompt=formatted_prompt)
            single_response = extract_llm_answer_from_full(raw_response)

            # Store the query and response in the database
            insert_query_response(
                conn=conn,
                query=query,
                response=raw_response,
                user_id=user_id
            )        

            # Update memory (chat history)
            chat_history.add_user_message(user_id, query)
            chat_history.add_ai_message(user_id, single_response)

            # Log memory usage
            current, peak = tracemalloc.get_traced_memory()
            log_debug(f"[MEMORY USAGE] Current: {current / 1024:.2f} KB; Peak: {peak / 1024:.2f} KB")

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
