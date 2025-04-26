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
    from controllers import convert_chunks_to_embedding  # fixed typo: convet -> convert
    from logs import log_error, log_info
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

chunks_to_embedding_routes = APIRouter()

@chunks_to_embedding_routes.post("/chunks_to_embedding", response_class=JSONResponse)
async def chunks_to_embedding(request: Request):
    """
    Convert text chunks to embeddings and store them in the database.
    """
    try:
        # Retrieve connection and model from app
        conn = getattr(request.app, "conn", None)
        embedding_model = getattr(request.app, "embedding_model", None)

        if not all([conn, embedding_model]):
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Application is not properly initialized."
            )

        # Pull chunks from the database
        chunks = pull_from_table(conn=conn, table_name="chunks", columns=["page_contest", "id"])
        if not chunks:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No chunks found in the database.")
        
        log_info(f"Pulled {len(chunks)} chunk(s) from the database.")
        for chunk in chunks:
            log_info(f"Chunk ID: {chunk['id']}, Content: {chunk['chunk'][:30]}...")
            # Convert chunks to embeddings
            embeddings = convert_chunks_to_embedding(chunks["chunk"], embedding_model)  # embeddings plural (many chunks)
            if not embeddings:
                raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to convert chunks to embeddings.")

        # Store the embeddings in the database
        insert_embedding(conn=conn, embeddings=embeddings, chunk_id=chunk["id"])  # fixed chunk_id reference

        return JSONResponse(content={"status": "success"}, status_code=HTTP_200_OK)

    except HTTPException as http_exc:
        # Re-raise FastAPI errors
        log_error(f"HTTPException in chunks_to_embedding: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Handle unexpected errors
        log_error(f"Unexpected error in chunks_to_embedding: {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
