import os
import sys
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from schemes import ChatManager

except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")


chat_mange_routes = APIRouter()

@chat_mange_routes.post("/chat/manage")
async def manage_chat_history(request: Request, body: ChatManager):
    """
    Manage the user's chat memory: reset or clear.
    Accepts parameters from ChatManager:
    - reset_memory (bool)
    - clear_chat (bool)
    """
    try:
        reset = body.reset_memory
        clear = body.clear_chat

        if reset:
            request.app.chat_manager.reset_memory()
            return JSONResponse(
                content={"message": "Memory reset successfully."},
                status_code=HTTP_200_OK
            )

        if clear:
            request.app.chat_manager.clear_chat_history()
            return JSONResponse(
                content={"message": "Chat history cleared successfully."},
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
