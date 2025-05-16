"""
Document Chunking API Endpoint.

This module provides FastAPI routes for converting documents into text chunks
and storing them in a SQLite database. It handles document processing,
chunking, and database operations.
"""

import sys

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

try:
    from src.utils import setup_main_path
    # Setup import path
    MAIN_DIR = setup_main_path(levels_up=2)
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.controllers import load_and_chunk, clear_table
    from src.schemes import ChunkRequest
    from src.dbs import insert_chunk
    from src.dependencies import get_db_conn

except ImportError as e:
    raise ImportError(
        f"[IMPORT ERROR] {__file__}: {e}"
    ) from e

to_chunks_route = APIRouter()


@to_chunks_route.post("/to_chunks")
async def to_chunks(
    body: ChunkRequest,
):
    """
    Converts documents into text chunks and stores them in the SQLite database.

    JSON body:
    {
        "file_path": "<optional_absolute_file_path>",
        "do_reset": 0 or 1
    }

    Returns:
        JSONResponse with inserted chunk count and metadata.
    """
    file_path = body.file_path
    do_reset = body.do_reset

    log_info(f"Starting chunking for: {file_path if file_path else '[ALL DOCUMENTS]'}")

    try:
        conn = Depends(get_db_conn)

        # Reset DB if requested (expected as int: 0 or 1)
        if do_reset == 1:
            clear_table(conn=conn, table_name="chunks")
            log_info("Chunks table cleared.")

        # Process files to DataFrame
        df = load_and_chunk(file_path=file_path)

        if df.empty:
            msg = "No valid documents found to process."
            log_error(msg)
            return JSONResponse(content={"status": "error", "message": msg}, status_code=404)

        # Insert into DB
        insert_chunk(conn=conn, data=df)
        log_info(f"Inserted {len(df)} chunks into the database.")

        return JSONResponse(
            content={
                "status": "success",
                "inserted_chunks": len(df),
                "documents": df.to_dict(orient="records")  # Ensures JSON-serializable output
            },
            status_code=200
        )

    except (ValueError, TypeError, AttributeError) as known_err:
        log_error(f"Handled exception in /to_chunks: {known_err}")
        return JSONResponse(
            content={"status": "error", "message": str(known_err)},
            status_code=500
        )
