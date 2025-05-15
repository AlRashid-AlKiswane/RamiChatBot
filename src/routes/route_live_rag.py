"""
Live RAG (Retrieval-Augmented Generation) API Endpoint

This module provides FastAPI routes for performing real-time RAG queries,
including query processing, embedding generation, and database retrieval.
"""

import logging
import sys
import sqlite3 as sql3
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)

# Setup import path and logging
try:
    from src.utils import setup_main_path
    MAIN_DIR = setup_main_path(levels_up=2)
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.embedding import EmbeddingModel
    from src.rag import search
    from src.schemes import LiveRAG
    from src.dependencies import get_db_conn, get_embedd

except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

live_rag_route = APIRouter()


@live_rag_route.post("/live_rag")
async def live_rag(
    request: LiveRAG,
    embedd: EmbeddingModel = Depends(get_embedd),
    conn: sql3.Connection = Depends(get_db_conn)
):
    """Handle live RAG query.
    
    Args:
        request: LiveRAG request parameters
        embedd: Embedding model instance
        conn: Database connection
        
    Returns:
        JSONResponse: Query results or error message
        
    Raises:
        HTTPException: 
            400 for invalid parameters
            404 if no results found
            500 for database or processing errors
    """
    query, top_k = request.query, request.top_k

    if not query or len(query.strip()) == 0:
        log_error("Query parameter is empty.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty."
        )

    if top_k <= 0:
        log_error(f"Invalid value for top_k: {top_k}.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="top_k must be greater than zero."
        )

    try:
        retriever_result = search(
            query=query,
            embedder=embedd,
            conn=conn,
            top_k=top_k
        )
        log_info(f"RAG query results: {retriever_result}")

        if not retriever_result:
            log_info(f"No results found for query: {query}")
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content={"message": "No results found for the query."}
            )

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "Retriever Results": [
                    one_ret["page_content"] for one_ret in retriever_result
                ]
            }
        )

    except sql3.DatabaseError as e:
        log_error(f"Database error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while processing the query."
        ) from e
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the query."
        ) from e
