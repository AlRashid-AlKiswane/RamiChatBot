import os
import sys
import threading
import time
import warnings
from fastapi import FastAPI
from logs import log_debug, log_error, log_info
from dotenv import load_dotenv

with warnings.catch_warnings():
    load_dotenv()
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    warnings.filterwarnings("ignore", category=ImportWarning)
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    warnings.filterwarnings("ignore", category=UnicodeWarning)
    warnings.filterwarnings("ignore", category=BytesWarning)
    warnings.filterwarnings("ignore", category=Warning)

# === Path Configuration ===
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from api import (
        hello_routes,
        upload_route,
        to_chunks_route,
        llms_config_route,
        generate_routes
    )
    from Database import (
        create_sqlite_engine,
        create_chunks_table,
        create_embeddings_table,
        create_query_responses_table
    )
    from utils import load_last_yaml
    from llm import HuggingFcaeModel

    from schemes import LLMResponse

except Exception as e:
    raise ImportError(f"Import Error in {__file__}: {e}")

# === FastAPI App ===
app = FastAPI(title="RamiChatBot API")

app.RETRIEVAL_CONTEXT =  "Hello Rami I'm AlRashid, How are you? Hello dear friend, I'm doing well."
# === Retry LLM Config & Model Loading in Background ===
def llm_init_loop():
    while True:
        try:
            app.LLM_CONFIG = load_last_yaml()
            if not app.LLM_CONFIG:
                log_error("[LLM CONFIG MISSING] No config found. Retrying in 10 seconds...")
                time.sleep(10)
                continue

            app.model = HuggingFcaeModel()
            app.model.init_llm(**app.LLM_CONFIG)
            log_info("[LLM] Model initialized successfully.")
            break
        except Exception as e:
            log_error(f"[LLM INIT ERROR] {e}")
            app.model = None
            time.sleep(10)


@app.on_event("startup")
async def startup_event():
    """Initialize DB, model config, and LLM instance on app startup."""
    log_info("[STARTUP] Initializing FastAPI application...")

    # === Start LLM Init Thread ===
    threading.Thread(target=llm_init_loop, daemon=True).start()

    # === Initialize SQLite Database ===
    try:
        app.conn = create_sqlite_engine()
        create_chunks_table(conn=app.conn)
        create_embeddings_table(conn=app.conn)
        create_query_responses_table(conn=app.conn)
        log_info("[DB] SQLite database and tables initialized.")
    except Exception as e:
        log_error(f"[DB INIT ERROR] {e}")


# === Include API Routers ===
app.include_router(hello_routes, prefix="/api", tags=["Hello"])
app.include_router(upload_route, prefix="/api", tags=["Upload File"])
app.include_router(to_chunks_route, prefix="/api", tags=["Documents to Chunks"])
app.include_router(llms_config_route, prefix="/api", tags=["LLMs Configs"])
app.include_router(generate_routes, prefix="/api", tags=["Chat Response"])


@app.on_event("shutdown")
async def shutdown_event():
    """Close DB connection on app shutdown."""
    log_info("[SHUTDOWN] Closing SQLite database connection...")
    if hasattr(app, 'conn'):
        app.conn.close()
        log_info("[DB] SQLite database connection closed.")
    else:
        log_error("[DB] No active database connection to close.")
