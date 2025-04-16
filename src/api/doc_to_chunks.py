from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import os
import sys
import pandas as pd

FILE_LOCATION = f"{os.path.dirname(__file__)}/doc_to_chunks.py"

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from config import get_settings, Settings
    from controllers import load_and_chunk
    from schemes import ChunkRequest
    from SQLite_database import create_sqlite_engine, insert_chunk
except Exception as e:
    msg = f"Import Error in: {FILE_LOCATION}, Error: {e}"
    raise ImportError(msg)

to_chunks_route = APIRouter()


@to_chunks_route.post("/to_chunks")
async def to_chunks(
    body: ChunkRequest,
    app_settings: Settings = Depends(get_settings)
):
    """
    Converts a document (or all documents in the folder) into text chunks and stores them in the SQLite database.

    Optional JSON body:
    {
        "file_path": "<optional_absolute_file_path>"
    }
    """
    file_path = body.file_path
    log_info(f"Starting chunking for: {file_path if file_path else '[ALL DOCUMENTS]'}")

    try:
        df = load_and_chunk(file_path=file_path)

        if df.empty:
            msg = "No valid documents found to process."
            log_error(msg)
            return JSONResponse(content={"status": "error", "message": msg}, status_code=404)

        conn = create_sqlite_engine()
        insert_chunk(conn=conn, data=df)

        log_info(f"Successfully inserted {len(df)} chunks into the database.")
        return JSONResponse(content={"status": "success", "inserted_chunks": len(df)}, status_code=200)

    except Exception as e:
        log_error(f"Unexpected error in /to_chunks endpoint: {e}")
        return JSONResponse(
            content={"status": "error", "message": "Internal server error"},
            status_code=500
        )
