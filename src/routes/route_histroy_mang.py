"""
Chat History Management API Endpoint.

This module provides a FastAPI route for managing user chat history and
clearing database tables such as chunks, embeddings, and query responses.
It supports both full and selective reset options via HTTP POST requests.
"""

import logging
import os
import sys
import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.schemes import ChatManager
    from src.historys import ChatHistoryManager
    from src.controllers import clear_table
    from src.dependencies import get_chat_history, get_db_conn

except ImportError as ie:
    logging.error("Import setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

chat_manage_routes = APIRouter()


@chat_manage_routes.post("/chat/manage")
# pylint: disable=too-many-arguments
async def manage_chat_history(
    body: ChatManager,
    reset_all: bool = False,
    remove_chunks: bool = False,
    remove_embeddings: bool = False,
    remove_query_response: bool = False,
    conn: sqlite3.Connection = Depends(get_db_conn),
    chat_manager: ChatHistoryManager = Depends(get_chat_history),
    user_id: Optional[str] = None
) -> JSONResponse:
    """
    Manage chat memory and database tables using specified reset options.

    This function handles user memory reset, chat history clearing, and table deletion.
    Operations can be triggered selectively or all at once using the 'reset_all' flag.

    Args:
        body (ChatManager): Request body with memory/chat reset flags.
        reset_all (bool): If True, resets everything (memory, chat, and DB tables).
        remove_chunks (bool): If True, clears the 'chunks' table.
        remove_embeddings (bool): If True, clears the 'embeddings' table.
        remove_query_response (bool): If True, clears the 'query_responses' table.
        conn (sqlite3.Connection): Dependency-injected DB connection.
        chat_manager (ChatHistoryManager): Dependency-injected chat history manager.
        user_id (str): Optional user identifier.

    Returns:
        JSONResponse: API response with a summary message.
    """
    try:
        actions = []
        message = "No action taken."

        # Extract from request body
        clear_chat = body.clear_chat
        reset_memory = body.reset_memory

        # Full reset logic
        if reset_all:
            if user_id:
                chat_manager.reset_memory(user_id)
                log_info("User memory reset.")
                chat_manager.clear_chat_history(user_id)
                log_info("User chat history cleared.")
                actions.extend(["memory_reset", "chat_clear"])

            for table in ["chunks", "embeddings", "query_responses"]:
                clear_table(conn, table)
                log_info(f"{table.capitalize()} table cleared.")
                actions.append(f"{table}_clear")

            message = "Full reset completed successfully."

        else:
            # Selective actions
            if reset_memory and user_id:
                chat_manager.reset_memory(user_id)
                log_info("User memory reset.")
                actions.append("memory_reset")

            if clear_chat and user_id:
                chat_manager.clear_chat_history(user_id)
                log_info("User chat history cleared.")
                actions.append("chat_clear")

            if remove_chunks:
                clear_table(conn, "chunks")
                log_info("Chunks table cleared.")
                actions.append("chunks_clear")

            if remove_embeddings:
                clear_table(conn, "embeddings")
                log_info("Embeddings table cleared.")
                actions.append("embeddings_clear")

            if remove_query_response:
                clear_table(conn, "query_responses")
                log_info("Query responses table cleared.")
                actions.append("query_responses_clear")

            if actions:
                message = f"Operations completed: {', '.join(actions)}"

        return JSONResponse(
            content={"message": message},
            status_code=HTTP_200_OK
        )

    except sqlite3.Error as e:
        log_error(f"[DATABASE ERROR] {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed."
        ) from e

    except Exception as e:
        log_error(f"[MANAGE CHAT HISTORY ERROR] {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred during chat management."
        ) from e
