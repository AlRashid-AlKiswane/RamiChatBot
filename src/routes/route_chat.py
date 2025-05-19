"""
Route module for handling chat generation requests using a Large Language Model (LLM) integrated
with Retrieval-Augmented Generation (RAG) context.

This module defines a FastAPI router that exposes a single POST endpoint `/chat` which receives a
user query and returns an AI-generated response. The response generation pipeline leverages
retrieved relevant context from a vector search (RAG), a prompt builder, and a HuggingFace-based
LLM for generating coherent and context-aware answers.

Main Features and Workflow:
---------------------------
1. Dependency Injection:
   Uses FastAPI's dependency injection to obtain essential components for request processing:
   - Database connection (`sqlite3.Connection`) for querying cached responses and saving new
     query-response pairs.
   - Chat history manager to retrieve and update conversation history per user.
   - Embedding model instance used to embed queries for vector search.
   - Pre-loaded HuggingFace LLM instance for text generation.

2. Request Handling:
   - Accepts a POST request with a JSON body conforming to the `Generate` schema, including the
     user's query.
   - Validates the query, ensuring it is not empty.
   - Checks for a cached response in the database to optimize latency and resource usage.
   - If a cached response exists, it is returned immediately.

3. Retrieval-Augmented Generation (RAG):
   - When no cached response is found, it performs a similarity search over stored documents
     (via the `search` function) to gather the most relevant context for the query.
   - The retrieved context enriches the prompt, providing the LLM with domain-specific or
     user-specific information to improve response quality.

4. Prompt Construction:
   - Utilizes `PromptBuilder` to create a custom prompt combining:
     * User conversation history,
     * Retrieved RAG context,
     * Current user message.

5. Response Generation:
   - Calls the LLM to generate a raw text response based on the constructed prompt.
   - Extracts the core answer from the full LLM output (using `extract_llm_answer_from_full`).
   - Updates the chat history by recording the user query and AI-generated response.
   - Persists the query-response pair into the database cache for future reuse.

6. Monitoring and Logging:
   - Tracks memory usage during generation using `tracemalloc`.
   - Logs key events such as cache hits/misses, prompt details, errors, and memory stats
     for observability and debugging.

7. Error Handling:
   - Raises appropriate HTTP exceptions (400 Bad Request for empty queries).
   - Logs and returns 500 Internal Server Error on unexpected failures while shielding
     internal details from the client.
   - Catches import errors explicitly to assist with debugging missing dependencies or
     misconfigurations at startup.

Usage:
------
- Designed to be mounted as part of a larger FastAPI app.
- Requires accompanying modules for logging, prompt construction, embedding, LLM, RAG search,
  chat history management, and database operations.
- Intended for chatbot or conversational AI systems where context-aware, cached, and efficient
  responses are required.

Example:
--------
POST /chat
{
  "query": "What are the store hours for Ramy Issa retail?"
}

Response:
{
  "status": "success",
  "response": "Our Ramy Issa stores are open from 9 AM to 9 PM every day."
}

Note:
-----
- This module assumes the presence of SQLite-based query response caching.
- The prompt name "rami_issa" is hardcoded and can be parameterized for different personas.
- The system currently retrieves top 5 context chunks during search; this number can be tuned.

Dependencies:
-------------
- FastAPI, Starlette
- SQLite3
- Custom modules: `logs`, `prompt`, `schemes`, `dbs`, `llm`, `embedding`, `historys`,
  `utils`, `rag`, `dependencies`
- HuggingFace transformers or compatible LLM backend
- `tracemalloc` for memory profiling

Author: Alrashid Issa
Date: 2025-05-15
"""

import logging
import os
import sys
import traceback
import tracemalloc
from sqlite3 import Connection
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_507_INSUFFICIENT_STORAGE
)


try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.dbs import insert_query_response, pull_from_table
    from src.dependencies import get_chat_history, get_db_conn, get_embedd, get_llm
    from src.embedding import EmbeddingModel
    from src.historys import ChatHistoryManager
    from src.llm import HuggingFaceLLM

    # Import internal modules
    from src.logs import log_debug, log_error, log_info
    from src.prompt import PromptBuilder
    from src.rag import search
    from src.schemes import Generate
    from src.utils import extract_llm_answer_from_full

except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

# Initialize router and memory profiler
generate_routes = APIRouter()
prompt_builder = PromptBuilder()
tracemalloc.start()


def _generate_new_response(user_id: str, query: str, dependencies: dict) -> str:
    """
    Generates a response from the LLM based on a user's query and conversation history.

    This function performs the following steps:
      - Retrieves relevant context from the knowledge base using semantic search.
      - Builds a prompt using the context, query, and chat history.
      - Generates a response using the specified LLM.
      - Stores the full response in the database.
      - Updates the chat history for the user.

    Args:
        user_id (str): Unique identifier for the user.
        query (str): The user's input question or message.
        dependencies (dict): A dictionary containing the following keys:
            - "conn" (Connection): SQLite database connection.
            - "chat_history" (ChatHistoryManager): Manages chat memory.
            - "embedd" (EmbeddingModel): Embedding model for vector search.
            - "llm" (HuggingFaceLLMs): The LLM used to generate the response.

    Returns:
        str: The final extracted response generated by the LLM.
    """
    conn = dependencies["conn"]
    chat_history = dependencies["chat_history"]
    embedd = dependencies["embedd"]
    llm = dependencies["llm"]

    context = search(query=query, conn=conn, embedder=embedd, top_k=5) or "Empty"
    log_debug(f"[LLM GENERATION] Context retrieved: {context}")

    formatted_prompt = prompt_builder.build_prompt(
        prompt_name="rami_issa",
        history=chat_history.get_chat_history(user_id),
        context=context,
        user_message=query,
    )

    raw_response = llm.generate_response(prompt=formatted_prompt)
    response = extract_llm_answer_from_full(raw_response)

    insert_query_response(
        conn=conn, query=query, response=raw_response, user_id=user_id
    )
    chat_history.add_user_message(user_id, query)
    chat_history.add_ai_message(user_id, response)

    return response


def get_all_dependencies(
    request: Request,
) -> Tuple[Connection, ChatHistoryManager, EmbeddingModel, HuggingFaceLLM]:
    """
    Dependency injector for FastAPI routes to provide required LLM tools and services.

    This function fetches and returns the necessary components for LLM-based response
    generation, including the database connection, chat history manager, embedding model,
    and language model.

    Args:
        request (Request): The current FastAPI request, used to extract context
                           for dependency resolution.

    Returns:
        Tuple[Connection, ChatHistoryManager, EmbeddingModel, HuggingFaceLLMs]: 
            A tuple containing the database connection, chat memory, embedder, and LLM.
    """
    return (
        get_db_conn(request),
        get_chat_history(request),
        get_embedd(request),
        get_llm(request),
    )


@generate_routes.post("/chat", response_class=JSONResponse)
async def generate_response(
    body: Generate,
    user_id: str,
    deps: Tuple[
        Connection, ChatHistoryManager, EmbeddingModel, HuggingFaceLLM
    ] = Depends(get_all_dependencies),
):
    """
    Generate a response from the LLM based on the user query with context retrieval.
    """
    try:
        conn, chat_history, embedd, llm = deps
        query = body.query

        if not query:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Query cannot be empty."
            )

        cached_response = pull_from_table(
            conn=conn, table_name="query_responses", columns=[], cach=(user_id, query)
        )

        if cached_response:
            response = extract_llm_answer_from_full(cached_response)
            if response:
                log_info(f"[CACHED HIT] Returning cached response for query: {query}")
                return JSONResponse(
                    content={"status": "success", "response": response},
                    status_code=HTTP_200_OK,
                )

        log_info(f"[CACHED MISS] No cached response found for query: {query}")
        response = _generate_new_response(
            user_id=user_id,
            query=query,
            dependencies={
                "conn": conn,
                "chat_history": chat_history,
                "embedd": embedd,
                "llm": llm,
            },
        )

        current, peak = tracemalloc.get_traced_memory()
        log_debug(
            f"[MEMORY USAGE] Current: {current / 1024:.2f} KB; Peak: {peak / 1024:.2f} KB"
        )

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"status": "success", "response": response},
        )

    except HTTPException as http_exc:
        log_error(f"[LLM GENERATION HTTP ERROR] {http_exc.detail}")
        raise http_exc

    except MemoryError as mem_err:
        log_error(f"[LLM GENERATION MEMORY ERROR] {mem_err}")
        return JSONResponse(
            status_code=HTTP_507_INSUFFICIENT_STORAGE,
            content={"status": "error", "message": "Memory allocation failed."},
        )

    except Exception as exc:  # pylint: disable=broad-exception-caught
        log_error(f"[LLM GENERATION UNKNOWN ERROR] {exc} {traceback.format_exc()}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "An unexpected error occurred while generating the response.",
            },
        )
