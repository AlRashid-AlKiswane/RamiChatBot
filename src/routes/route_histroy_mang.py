import os
import sys
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from typing import Optional

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from schemes import ChatManager
    from historys import ChatHistoryManager
    from controllers import clear_table

except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")


def get_db_conn(request: Request):
    """Retrieve the relational database connection from the app state."""
    conn = getattr(request.app.state, "conn", None)
    if not conn:
        log_debug("Relational database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Relational database service is not available."
        )
    return conn

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

chat_manage_routes = APIRouter()


@chat_manage_routes.post("/chat/manage")
async def manage_chat_history(
    request: Request,
    body: ChatManager,
    conn: sqlite3.Connection = Depends(get_db_conn),
    chat_manager: ChatHistoryManager = Depends(get_chat_history),
    user_id: Optional[str] = None,
    remove_chunks: Optional[bool] = False,
    remove_embeddings: Optional[bool] = False,
    remove_query_response: Optional[bool] = False,
    reseting: Optional[bool] = False,
):
    """
    Manage the user's chat memory or clear database tables.

    Accepts:
    - reset_memory: bool (from ChatManager)
    - clear_chat: bool (from ChatManager)
    - user_id: str
    - remove_chunks: bool
    - remove_embeddings: bool
    - remove_query_response: bool
    - reseting: bool (shortcut for all clear/reset options)
    """
    try:
        # Shortcut to reset all
        if reseting:
            if user_id:
                chat_manager.reset_memory(user_id)
                chat_manager.clear_chat_history(user_id)
            clear_table(conn=conn, table_name="chunks")
            clear_table(conn=conn, table_name="embeddings")
            clear_table(conn=conn, table_name="query_responses")

            return JSONResponse(
                content={"message": "Full reset completed successfully."},
                status_code=HTTP_200_OK
            )

        # Individual controls
        if body.reset_memory and user_id:
            chat_manager.reset_memory(user_id)
            log_info("Memory reset.")
            return JSONResponse(
                content={"message": "Memory reset successfully."},
                status_code=HTTP_200_OK
            )

        if body.clear_chat and user_id:
            chat_manager.clear_chat_history(user_id)
            log_info("Chat history cleared.")
            return JSONResponse(
                content={"message": "Chat history cleared successfully."},
                status_code=HTTP_200_OK
            )

        if remove_chunks:
            clear_table(conn=conn, table_name="chunks")
            log_info("Chunks table cleared.")
            return JSONResponse(
                content={"message": "Chunks cleared successfully."},
                status_code=HTTP_200_OK
            )

        if remove_embeddings:
            clear_table(conn=conn, table_name="embeddings")
            log_info("Embedding table cleared.")
            return JSONResponse(
                content={"message": "Embeddings cleared successfully."},
                status_code=HTTP_200_OK
            )

        if remove_query_response:
            clear_table(conn=conn, table_name="query_responses")
            log_info("Query responses table cleared.")
            return JSONResponse(
                content={"message": "Query responses cleared successfully."},
                status_code=HTTP_200_OK
            )

        return JSONResponse(
            content={"message": "No action taken."},
            status_code=HTTP_200_OK
        )

    except Exception as e:
        log_error(f"[CHAT HISTORY MANAGE ERROR] {e}")
        return JSONResponse(
            content={"message": "Failed to manage chat history."},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )