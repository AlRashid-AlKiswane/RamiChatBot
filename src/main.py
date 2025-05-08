import os
import sys
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(MAIN_DIR)

from src.logs import log_debug, log_error, log_info

# === Import Routes ===
from routes import (
    hello_routes, upload_route, to_chunks_route, llm_settings_route,
    generate_routes, chat_manage_routes, chunks_to_embedding_routes,
    monitor_router, logers_router
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
app.include_router(upload_route, prefix="/api", tags=["File Upload"])
app.include_router(to_chunks_route, prefix="/api", tags=["Text Chunking"])
app.include_router(chunks_to_embedding_routes, prefix="/api", tags=["Embeddings"])
app.include_router(llm_settings_route, prefix="/api", tags=["LLM Settings"])
app.include_router(generate_routes, prefix="/api", tags=["Text Generation"])
app.include_router(chat_manage_routes, prefix="/api", tags=["Chat Management"])
app.include_router(monitor_router, prefix="/api", tags=["Monitoring"])
app.include_router(logers_router, prefix="/api", tags=["Logging"])

# Add the template rendere 
templates = Jinja2Templates(directory=f"{MAIN_DIR}/src/web")

# Serve all HTML pages
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    # List of allowed pages for security
    allowed_pages = {
        "hello": "hello.html",
        "upload": "upload.html",
        "to_chunks": "to_chunks.html",
        "chunks_to_embedding": "chunks_to_embedding.html",
        "llms_config": "llms_config.html",
        "chat_manager": "chat_manager.html",
        "monitoring": "monitoring.html"
    }
    
    if page_name not in allowed_pages:
        return templates.TemplateResponse("404.html", {"request": request})
    
    return templates.TemplateResponse(f"html/{allowed_pages[page_name]}", {"request": request})

