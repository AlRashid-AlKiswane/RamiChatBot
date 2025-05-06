from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
import os
import sys

FILE_LOCATION = f"{os.path.dirname(__file__)}/doc_to_chunks.py"

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
    from config import get_settings, Settings
    from controllers import load_and_chunk, clear_table
    from schemes import ChunkRequest
    from dbs import insert_chunk
except Exception as e:
    raise ImportError(f"Import Error in: {FILE_LOCATION}, Error: {e}")

to_chunks_route = APIRouter()


@to_chunks_route.post("/to_chunks")
async def to_chunks(
    request: Request,
    body: ChunkRequest,
    app_settings: Settings = Depends(get_settings)
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
        conn = getattr(request.app.state, "conn", None)

        # Reset DB if requested (expected as int: 0 or 1)
        if do_reset == 1:
            clear_table(conn=conn, table_name="chunks")
            clear_table(conn=conn, table_name="embeddings")
            log_info("Chunks table cleared.")
            log_info("Embeddings table cleared.")


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

    except Exception as e:
        log_error(f"Unexpected error in /to_chunks endpoint: {e}")
        return JSONResponse(
            content={"status": "error", "message": "Internal server error"},
            status_code=500
        )
