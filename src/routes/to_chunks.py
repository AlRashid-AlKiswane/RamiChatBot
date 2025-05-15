"""
Document Chunking API Endpoint.

This module provides FastAPI routes for converting documents into text chunks
and storing them in a SQLite database. It handles document processing,
chunking, and database operations.
"""

import logging
import os
import sys
from sqlite3 import Connection

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

FILE_LOCATION = f"{os.path.dirname(__file__)}/doc_to_chunks.py"

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.helpers import get_settings, Settings
    from src.controllers import load_and_chunk, clear_table
    from src.schemes import ChunkRequest
    from src.dbs import insert_chunk
    from src.dependencies import get_db_conn

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

to_chunks_route = APIRouter()

@to_chunks_route.post("/to_chunks")
async def to_chunks(
    body: ChunkRequest,
    app_settings: Settings = Depends(get_settings),
    conn: Connection = Depends(get_db_conn)
) -> JSONResponse:
    """Convert documents to chunks and store in database.

    Args:
        request: FastAPI Request object
        body: ChunkRequest containing file_path and reset flag
        app_settings: Application settings (dependency injection)

    Returns:
        JSONResponse: Operation result with status and metadata

    Example Request Body:
        {
            "file_path": "/path/to/document.pdf",
            "do_reset": 1
        }
    """
    file_path = body.file_path
    do_reset = body.do_reset

    log_info(f"Starting chunking for: {file_path if file_path else '[ALL DOCUMENTS]'}")

    try:
        # Reset DB if requested (expected as int: 0 or 1)
        if do_reset == 1:
            clear_table(conn=conn, table_name="chunks")
            log_info("Chunks table cleared.")

        # Process files to DataFrame
        # pylint: disable=unexpected-keyword-arg
        df = load_and_chunk(file_path=file_path,
                            settings=app_settings)

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
                "documents": df.to_dict(orient="records")
            },
            status_code=200
        )

    except FileNotFoundError as e:
        log_error(f"File not found error: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=404
        )
    except ValueError as e:
        log_error(f"Validation error: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=400
        )
    except Exception as e:  # pylint: disable=broad-except
        log_error(f"Unexpected error in /to_chunks endpoint: {e}")
        return JSONResponse(
            content={"status": "error", "message": "Internal server error"},
            status_code=500
        )
