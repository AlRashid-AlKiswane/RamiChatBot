import os
import threading
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_200_OK

from src.logs import log_debug, log_error, log_info

# === Import Routes ===
from routes import (
    hello_routes, upload_route, to_chunks_route, llm_settings_route,
    generate_routes, chat_manage_routes, chunks_to_embedding_routes,
    monitor_router
)

# === DB and LLM Initialization ===
from dbs import (
    create_sqlite_engine, create_chunks_table, create_embeddings_table,
    create_query_responses_table
)
from embedding import EmbeddingModel
from utils import load_last_yaml
from historys import ChatHistoryManager

# === FastAPI App ===


app = FastAPI()

# === Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    log_info("[STARTUP] Initializing FastAPI app and components...")

    try:
        app.state.conn = create_sqlite_engine()
        create_chunks_table(conn=app.state.conn)
        create_embeddings_table(conn=app.state.conn)
        create_query_responses_table(conn=app.state.conn)

        app.state.embedding_model = EmbeddingModel()
        app.state.llm = None  # Will be loaded later
        app.state.chat_manager = ChatHistoryManager()
        app.state.RETRIEVAL_CONTEXT = "No relevant context found."

        log_info("[DB] SQLite database initialized successfully.")
    except Exception as e:
        log_error(f"[STARTUP ERROR] Failed to initialize resources: {e}")
        app.state.conn = None
        app.state.embedding_model = None
        app.state.model = None
        app.state.chat_manager = None


@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully close resources."""
    log_info("[SHUTDOWN] Cleaning up application resources...")

    conn = getattr(app.state, "conn", None)
    if conn:
        conn.close()
        log_info("[DB] Connection closed successfully.")
    else:
        log_error("[DB] No active DB connection found.")

# === Include Routers ===
app.include_router(hello_routes, prefix="/api", tags=["Hello"])
app.include_router(upload_route, prefix="/api", tags=["Upload File"])
app.include_router(to_chunks_route, prefix="/api", tags=["Chunks"])
app.include_router(chunks_to_embedding_routes, prefix="/api", tags=["Embedding"])
app.include_router(llm_settings_route, prefix="/api", tags=["LLM Config"])
app.include_router(generate_routes, prefix="/api", tags=["Chat Generation"])
app.include_router(chat_manage_routes, prefix="/api", tags=["Chat Management"])
app.include_router(monitor_router, prefix="/api", tags=["Monitroy System"])

