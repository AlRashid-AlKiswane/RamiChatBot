"""Dependency management for chat application.

This module handles:
- System path setup for the application
- Safe importing of required modules
- Dependency injection container for chat components
"""

import logging
import sys
import sqlite3
from typing import Any
from fastapi import Request, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

# Setup system path
try:
    from utils import setup_main_path, safe_import

    MAIN_PATH = setup_main_path(levels_up=2)
    sys.path.append(MAIN_PATH)

    # Safe imports
    embedding_module = safe_import("src.embedding.sentence_model")
    history_module = safe_import("src.historys.chathistroy")
    llm_module = safe_import("src.llm.hg_llms")

    EmbeddingModel = embedding_module.EmbeddingModel
    ChatHistoryManager = history_module.ChatHistoryManager
    HuggingFaceLLMs = llm_module.HuggingFaceLLMs

    from src.logs import log_debug

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
    raise
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
    raise
except Exception as e:
    logging.critical("Unexpected error during dependency setup", exc_info=True)
    raise


def get_llm(request: Request) -> Any:
    """Retrieve the LLM instance from the app state."""
    llm = getattr(request.app.state, "llm", None)
    if not llm:
        log_debug("LLM instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM service is not initialized. Please configure via /llmsSettings."
        )
    return llm


def get_db_conn(request: Request) -> sqlite3.Connection:
    """Retrieve the database connection from the app state."""
    conn = getattr(request.app.state, "conn", None)
    if not conn:
        log_debug("Database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database service unavailable."
        )
    return conn


def get_embedd(request: Request) -> Any:
    """Retrieve the embedding model from the app state."""
    embedding = getattr(request.app.state, "embedding_model", None)
    if not embedding:
        log_debug("Embedding model not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding service unavailable."
        )
    return embedding


def get_chat_history(request: Request) -> Any:
    """Retrieve the chat history manager from the app state."""
    chat_history = getattr(request.app.state, "chat_manager", None)
    if not chat_history:
        log_debug("Chat history manager not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat history service unavailable."
        )
    return chat_history
