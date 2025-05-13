import os
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.logs import log_error, log_info
from routes import (
    chat_manage_routes,
    chunks_to_embedding_routes,
    crawler_route,
    generate_routes,
    hello_routes,
    live_rag_route,
    llm_settings_route,
    logers_router,
    monitor_router,
    to_chunks_route,
    upload_route,
)
from historys import ChatHistoryManager
from embedding import EmbeddingModel
from dbs import (
    create_chunks_table,
    create_embeddings_table,
    create_query_responses_table,
    create_sqlite_engine,
)

# === Path Setup ===
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(MAIN_DIR)

# === FastAPI App Initialization ===
app = FastAPI()

# === Middleware Configuration ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application resources on startup."""
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


# === Include API Routers ===
app.include_router(hello_routes, prefix="/api", tags=["Hello"])
app.include_router(upload_route, prefix="/api", tags=["File Upload"])
app.include_router(to_chunks_route, prefix="/api", tags=["Text Chunking"])
app.include_router(chunks_to_embedding_routes, prefix="/api", tags=["Embeddings"])
app.include_router(llm_settings_route, prefix="/api", tags=["LLM Settings"])
app.include_router(generate_routes, prefix="/api", tags=["Text Generation"])
app.include_router(chat_manage_routes, prefix="/api", tags=["Chat Management"])
app.include_router(monitor_router, prefix="/api", tags=["Monitoring"])
app.include_router(logers_router, prefix="/api", tags=["Logging"])
app.include_router(crawler_route, prefix="/api", tags=["Crawler in Web Pages"])
app.include_router(live_rag_route, prefix="/api", tags=["Live RAG"])

# === Template Configuration ===
templates = Jinja2Templates(directory=f"{MAIN_DIR}/src/web")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    """Serve one of the predefined HTML pages."""
    allowed_pages = {
        "hello": "hello.html",
        "upload": "upload.html",
        "to_chunks": "to_chunks.html",
        "chunks_to_embedding": "chunks_to_embedding.html",
        "llms_config": "llms_config.html",
        "chat_manager": "chat_manager.html",
        "monitoring": "monitoring.html",
        "chat": "chat.html",
        "crawl": "crawl.html",
        "rag": "rag.html",
    }

    if page_name not in allowed_pages:
        return templates.TemplateResponse("404.html", {"request": request})

    return templates.TemplateResponse(
        f"html/{allowed_pages[page_name]}", {"request": request}
    )
