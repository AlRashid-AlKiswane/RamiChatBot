"""
Chat History Management API Endpoint.

This module provides FastAPI routes for managing user chat history and
clearing database tables like chunks, embeddings, and query responses.
"""

import logging
import os
import sys
import sqlite3
from typing import Optional
from dataclasses import dataclass
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.schemes import ChatManager
    from src.historys import ChatHistoryManager
    from src.controllers import clear_table
    from src.dependencies import get_chat_history, get_db_conn

except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

chat_manage_routes = APIRouter()


@dataclass
class ResetOperations:
    """Class to hold reset operation parameters."""
    remove_chunks: bool = False
    remove_embeddings: bool = False
    remove_query_response: bool = False
    reset_memory: bool = False
    clear_chat: bool = False
    reset_all: bool = False


def _clear_database_tables(conn: sqlite3.Connection, ops: ResetOperations) -> None:
    """Clear specified database tables."""
    if ops.reset_all or ops.remove_chunks:
        clear_table(conn=conn, table_name="chunks")
        log_info("Chunks table cleared.")

    if ops.reset_all or ops.remove_embeddings:
        clear_table(conn=conn, table_name="embeddings")
        log_info("Embedding table cleared.")

    if ops.reset_all or ops.remove_query_response:
        clear_table(conn=conn, table_name="query_responses")
        log_info("Query responses table cleared.")


def _clear_chat_data(chat_manager: ChatHistoryManager, user_id: str, ops: ResetOperations) -> None:
    """Clear chat-related data."""
    if ops.reset_all or ops.reset_memory:
        chat_manager.reset_memory(user_id)
        log_info("Memory reset.")

    if ops.reset_all or ops.clear_chat:
        chat_manager.clear_chat_history(user_id)
        log_info("Chat history cleared.")


def perform_resets(
    chat_manager: ChatHistoryManager,
    conn: sqlite3.Connection,
    user_id: Optional[str],
    ops: ResetOperations
) -> JSONResponse:
    """Perform various reset operations based on the provided parameters.
    
    Args:
        chat_manager: Chat history manager instance
        conn: Database connection
        user_id: ID of the user to perform operations for
        ops: Reset operations configuration
    
    Returns:
        JSONResponse with operation status
    
    Raises:
        sqlite3.Error: For database operations failures
    """
    try:
        message = "No action taken."
        actions = []

        if ops.reset_all:
            if user_id:
                _clear_chat_data(chat_manager, user_id, ops)
            _clear_database_tables(conn, ops)
            message = "Full reset completed successfully."
            actions.append("full_reset")
        else:
            if user_id:
                if ops.reset_memory:
                    _clear_chat_data(chat_manager, user_id, ops)
                    message = "Memory reset successfully."
                    actions.append("memory_reset")
                if ops.clear_chat:
                    _clear_chat_data(chat_manager, user_id, ops)
                    message = "Chat history cleared successfully."
                    actions.append("chat_clear")

            _clear_database_tables(conn, ops)
            if ops.remove_chunks:
                actions.append("chunks_clear")
            if ops.remove_embeddings:
                actions.append("embeddings_clear")
            if ops.remove_query_response:
                actions.append("query_responses_clear")

            if actions:
                message = "Operations completed: " + ", ".join(actions)

        return JSONResponse(
            content={"message": message},
            status_code=HTTP_200_OK
        )

    except sqlite3.Error as db_err:
        log_error(f"[SQLITE ERROR] {db_err}")
        raise
    except Exception as exc:
        log_error(f"[PERFORM RESETS ERROR] {exc}")
        raise


@chat_manage_routes.post("/chat/manage")
async def manage_chat_history(
    request_data: ChatManager,
    conn: sqlite3.Connection = Depends(get_db_conn),
    chat_manager: ChatHistoryManager = Depends(get_chat_history),
    user_id: Optional[str] = None
) -> JSONResponse:
    """Manage the user's chat memory or clear database tables.
    
    Args:
        request_data: ChatManager model with all reset options
        conn: Database connection
        chat_manager: Chat history manager
        user_id: Optional user ID
    
    Returns:
        JSONResponse with operation result
    
    Raises:
        HTTPException: If an error occurs during operations
    """
    try:
        ops = ResetOperations(
            remove_chunks=request_data.remove_chunks,
            remove_embeddings=request_data.remove_embeddings,
            remove_query_response=request_data.remove_query_response,
            reset_memory=request_data.reset_memory,
            clear_chat=request_data.clear_chat,
            reset_all=request_data.reset_all
        )

        return perform_resets(
            chat_manager=chat_manager,
            conn=conn,
            user_id=user_id,
            ops=ops
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
            detail="An unexpected error occurred while managing chat history."
        ) from e
