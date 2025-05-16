"""
Chunks to Embedding Conversion API Endpoint

This module provides FastAPI routes for converting text chunks to embeddings
and storing them in the database.
"""

import sys
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

try:
    from src.utils import setup_main_path

    # Setup import path
    MAIN_DIR = setup_main_path(levels_up=2)
    sys.path.append(MAIN_DIR)

    from dbs import pull_from_table, insert_embedding
    from logs import log_error, log_info
    from embedding import EmbeddingModel

except ImportError as import_err:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {import_err}") from import_err

chunks_to_embedding_routes = APIRouter()


@chunks_to_embedding_routes.post("/chunks_to_embedding", response_class=JSONResponse)
async def chunks_to_embedding(request: Request):
    """
    Convert text chunks to embeddings and store them in the database.

    Args:
        request (Request): FastAPI request object with app state.

    Returns:
        JSONResponse: Success or error status message.
    """
    try:
        conn = getattr(request.app.state, "conn", None)
        embedding_model: EmbeddingModel = getattr(request.app.state, "embedding_model", None)

        if conn is None or embedding_model is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection or embedding model not initialized.",
            )

        chunks = pull_from_table(conn=conn, table_name="chunks", columns=["page_contest", "id"])
        if not chunks:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="No chunks found in the database.",
            )

        log_info(f"Pulled {len(chunks)} chunk(s) from the database.")

        for chunk in chunks:
            embedding = embedding_model.embed(text=chunk["text"])
            insert_embedding(conn=conn, embedding=embedding.tolist(), chunk_id=chunk["id"])

        return JSONResponse(content={"status": "success"}, status_code=HTTP_200_OK)

    except HTTPException as http_exc:
        log_error(f"HTTPException in chunks_to_embedding: {http_exc.detail}")
        raise http_exc

    except AttributeError as ae:
        log_error(f"Specific error in chunks_to_embedding: {ae}")
        return JSONResponse(
            content={"status": "error", "detail": str(ae)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except (ValueError, TypeError) as specific_err:
        log_error(f"Expected error in chunks_to_embedding: {specific_err}")
        return JSONResponse(
            content={"status": "error", "detail": str(specific_err)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
