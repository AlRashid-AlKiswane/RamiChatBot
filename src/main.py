import os
import threading
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK
from src.logs import log_debug, log_error, log_info

# === Import Routes ===
from api import (
    hello_routes, upload_route, to_chunks_route, llms_config_route,
    generate_routes, chat_manage_routes, chunks_to_embedding_routes,
)

# === DB and LLM Initialization ===
from dbs import (
    create_sqlite_engine, create_chunks_table, create_embeddings_table,
    create_query_responses_table, create_cache_table,
)
from embedding import EmbeddingModel
from utils import load_last_yaml
from llm import HuggingFaceModel, LlamaCPP  # Fixed class name spelling
from schemes import Application
from historys import ChatHistoryManager

# === FastAPI App ===
app = FastAPI(title="RamiChatBot API")

# === Shared State ===
app.chat_manager = ChatHistoryManager()
app.RETRIEVAL_CONTEXT = "No context available."
app.model_name = None
app.config_path = None
app.model_initialized = False
app.model_init_event = threading.Event()
app.model_lock = threading.Lock()

@app.post("/application")
async def application(body: Application):
    """Receive model application parameters."""
    state = app

    if state.model_initialized and body.model_name == state.model_name and body.config_path == state.config_path:
        log_info("[APPLICATION] Model already initialized with the same parameters.")
        return JSONResponse(
            content={"message": "Model is already initialized."},
            status_code=HTTP_200_OK
        )

    state.model_name = body.model_name
    state.config_path = body.config_path
    state.model_init_event.set()

    log_info("[APPLICATION] New application parameters received.")
    return JSONResponse(
        content={"message": "Application parameters passed successfully."},
        status_code=HTTP_200_OK
    )

def llm_init_loop():
    """Background thread to initialize LLM based on config and model name."""
    while True:
        app.model_init_event.wait()
        app.model_init_event.clear()

        model_name = app.model_name
        config_path = app.config_path

        if not model_name or not config_path:
            log_error("[LLM INIT] Model name or config path missing.")
            time.sleep(5)
            continue

        try:
            config = load_last_yaml(file_path=config_path)
            if not config:
                log_error("[LLM INIT] Config file is empty or invalid.")
                continue

            if model_name == "huggingface":
                model = HuggingFaceModel()
            elif model_name == "llama_cpp":
                model = LlamaCPP()
            else:
                log_error(f"[LLM INIT] Unknown model name: {model_name}")
                continue

            model.init_llm(**config)
            app.LLM_CONFIG = config
            app.model = model
            app.model_initialized = True
            log_info("[LLM INIT] Model initialized successfully.")

        except Exception as e:
            log_error(f"[LLM INIT ERROR] {e}")
            app.model = None
            app.model_initialized = False
            time.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Initialize database and start model background loader."""
    log_info("[STARTUP] Initializing FastAPI application...")

    # Start model initialization background thread
    threading.Thread(target=llm_init_loop, daemon=True).start()
    log_info("[LLM INIT] Background LLM initializer thread started.")

    try:
        app.conn = create_sqlite_engine()
        create_chunks_table(conn=app.conn)
        create_embeddings_table(conn=app.conn)
        create_query_responses_table(conn=app.conn)
        create_cache_table(conn=app.conn)
        app.embedding_model = EmbeddingModel()
        log_info("[DB] SQLite database and tables initialized.")
    except Exception as e:
        log_error(f"[DB INIT ERROR] {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close DB connection on shutdown."""
    log_info("[SHUTDOWN] Closing resources...")
    conn = getattr(app, "conn", None)
    if conn:
        conn.close()
        log_info("[DB] SQLite connection closed.")
    else:
        log_error("[DB] No active DB connection found.")

# === Include Routers ===
app.include_router(hello_routes, prefix="/api", tags=["Hello"])
app.include_router(upload_route, prefix="/api", tags=["Upload File"])
app.include_router(to_chunks_route, prefix="/api", tags=["Documents to Chunks"])
app.include_router(llms_config_route, prefix="/api", tags=["LLMs Configs"])
app.include_router(generate_routes, prefix="/api", tags=["Chat Response"])
app.include_router(chat_manage_routes, prefix="/api", tags=["Chat Management"])
app.include_router(chunks_to_embedding_routes, prefix="/api", tags=["Chunks to Embedding"])