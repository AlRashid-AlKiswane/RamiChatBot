import os
import sys
import sqlite3 as sql3
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from dbs import pull_from_table
    from embedding import EmbeddingModel
    from rag import search
    from schemes import LiveRAG

except ImportError as e:
    log_error(f"[IMPORT ERROR] {__file__}: {e}")
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

live_rag_route = APIRouter()

def get_db_conn(request: Request):
    """Retrieve the relational database connection from the app state."""
    conn = request.app.state.conn
    if not conn:
        log_error("Relational database connection not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Relational database service is not available."
        )
    return conn

def get_embedd(request: Request):
    """Retrieve the embedding model instance from the app state."""
    embedding = request.app.state.embedding_model
    if not embedding:
        log_error("Embedding model instance not found in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding model service is not available."
        )
    return embedding

@live_rag_route.post("/live_rag")
async def live_rag(request: LiveRAG, embedd: EmbeddingModel = Depends(get_embedd), conn: sql3.Connection = Depends(get_db_conn)):
    """Handle live RAG query."""
    query, top_k = request.query, request.top_k
    
    # Validate query parameter
    if not query or len(query.strip()) == 0:
        log_error("Query parameter is empty.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty."
        )

    # Validate top_k value
    if top_k <= 0:
        log_error(f"Invalid value for top_k: {top_k}. It must be greater than zero.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="top_k must be greater than zero."
        )
    
    try:
        # Perform the search operation
        retriever_result = search(query=query, embedder=embedd, conn=conn, top_k=top_k)
        log_info(retriever_result)
        # Check if no results found
        if not retriever_result:
            log_info(f"No results found for query: {query}")
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content={"message": "No results found for the query."}
            )

        # Return results if found
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"Retriever Results": [one_ret["page_content"] for one_ret in retriever_result]}
        )


    except sql3.DatabaseError as e:
        log_error(f"Database error while processing the RAG query: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while processing the query."
        )
    except Exception as e:
        log_error(f"An unexpected error occurred while processing the RAG query: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the query."
        )
