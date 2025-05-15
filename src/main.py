"""
Main FastAPI application entry point with authentication, routing, and startup configuration.
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from logs import log_error, log_info
from routes import (
    chat_manage_routes, chunks_to_embedding_routes, crawler_route,
    generate_routes, hello_routes, live_rag_route, llm_settings_route,
    logers_router, monitor_router, to_chunks_route, upload_route
)
from historys import ChatHistoryManager
from embedding import EmbeddingModel
from dbs import (
    create_chunks_table, create_embeddings_table,
    create_query_responses_table, create_sqlite_engine
)

# Path Setup
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(MAIN_DIR)

# FastAPI Initialization
app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory=os.path.join(MAIN_DIR, "src/web"))

# Startup Event
@app.on_event("startup")
async def startup_event():
    log_info("[startup_event] Initializing FastAPI app.")
    try:
        app.state.conn = create_sqlite_engine()
        create_chunks_table(conn=app.state.conn)
        create_embeddings_table(conn=app.state.conn)
        create_query_responses_table(conn=app.state.conn)

        app.state.embedding_model = EmbeddingModel()
        app.state.llm = None
        app.state.chat_manager = ChatHistoryManager()
        app.state.RETRIEVAL_CONTEXT = "No relevant context found."

        log_info("[startup_event] Initialization completed successfully.")
    except Exception as exc:
        log_error(f"[startup_event] Initialization failed: {exc}")
        raise

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    log_info("[shutdown_event] Shutting down FastAPI app.")
    try:
        conn = getattr(app.state, "conn", None)
        if conn:
            conn.close()
            log_info("[shutdown_event] SQLite connection closed.")
    except Exception as exc:
        log_error(f"[shutdown_event] Error while closing resources: {exc}")

# Include All Routes Publicly
all_routes = [
    hello_routes, upload_route, to_chunks_route, chunks_to_embedding_routes,
    llm_settings_route, generate_routes, chat_manage_routes,
    monitor_router, logers_router, crawler_route, live_rag_route
]
for route in all_routes:
    app.include_router(route, prefix="/api")

# Public Pages
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("html/login.html", {"request": request})

@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    allowed_pages = {
        "index": "index.html",
        "hello": "hello.html", 
        "upload": "upload.html",
        "to_chunks": "to_chunks.html",
        "chunks_to_embedding": "chunks_to_embedding.html",
        "llms_config": "llms_config.html",
        "monitoring": "monitoring.html",
        "chat": "chat.html", 
        "crawl": "crawl.html",
        "rag": "rag.html", 
        "chat_manager":"chat_manager.html"
    }

    template_name = allowed_pages.get(page_name)
    if not template_name:
        return templates.TemplateResponse("html/404.html", {"request": request}, status_code=404)

    template_path = f"html/{template_name}" if template_name != "index.html" else template_name
    return templates.TemplateResponse(template_path, {"request": request})

# Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log_error(f"[validation_exception_handler] Validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )