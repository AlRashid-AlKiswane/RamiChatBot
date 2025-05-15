"""
Chunks to Embedding Conversion API Endpoint

This module provides FastAPI routes for converting text chunks to embeddings
and storing them in the database.
"""

import os
import sys
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from dbs import pull_from_table, insert_embedding
    from logs import log_error, log_info
    from embedding import EmbeddingModel
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

chunks_to_embedding_routes = APIRouter()

@chunks_to_embedding_routes.post("/chunks_to_embedding", response_class=JSONResponse)
async def chunks_to_embedding(request: Request):
    """
    Convert text chunks to embedding and store them in the database.
    """
    try:
        # Retrieve connection and model from app
        conn = getattr(request.app.state, 'conn', None)
        embedding_model: EmbeddingModel = getattr(request.app.state, 'embedding_model', None)

        # Pull chunks from the database
        chunks = pull_from_table(conn=conn, table_name="chunks", columns=["page_contest", "id"])
        if not chunks:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No chunks found in the database.")
        
        log_info(f"Pulled {len(chunks)} chunk(s) from the database.")
        for chunk in chunks:
            # Convert chunks to embedding
            embedding = embedding_model.embed(text=chunk["text"])

            # Store the embedding in the database
            insert_embedding(conn=conn, embedding=embedding.tolist(), chunk_id=chunk["id"])

        return JSONResponse(content={"status": "success"}, status_code=HTTP_200_OK)

    except HTTPException as http_exc:
        # Re-raise FastAPI errors
        log_error(f"HTTPException in chunks_to_embedding: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Handle unexpected errors
        log_error(f"Unexpected error in chunks_to_embedding: {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
