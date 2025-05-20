"""
Main FastAPI application entry point with authentication, routing, and startup configuration.
"""

import logging
import os
import sys

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.enums import MainAppLogMessages
    from src.routes import (
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
    from src.historys import ChatHistoryManager
    from src.embedding import EmbeddingModel
    from src.dbs import (
        create_chunks_table,
        create_embeddings_table,
        create_query_responses_table,
        create_sqlite_engine,
    )
except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 Templates
templates = Jinja2Templates(directory=os.path.join(MAIN_DIR, "src/web"))


@app.on_event("startup")
async def startup_event():
    """Initialize application state and resources on startup."""
    log_info(MainAppLogMessages.STARTUP_BEGIN.value)
    try:
        app.state.conn = create_sqlite_engine()
        create_chunks_table(conn=app.state.conn)
        create_embeddings_table(conn=app.state.conn)
        create_query_responses_table(conn=app.state.conn)

        app.state.embedding_model = EmbeddingModel()
        app.state.llm = None
        app.state.chat_manager = ChatHistoryManager()
        app.state.RETRIEVAL_CONTEXT = "No relevant context found."

        log_info(MainAppLogMessages.STARTUP_SUCCESS.value)
    except (RuntimeError, ValueError, IOError) as exc:  # Replace with specific exceptions
        log_error(f"{MainAppLogMessages.STARTUP_FAIL.value} {exc}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    log_info(MainAppLogMessages.SHUTDOWN_BEGIN.value)
    try:
        conn = getattr(app.state, "conn", None)
        if conn:
            conn.close()
            log_info(MainAppLogMessages.SHUTDOWN_DB_CLOSED.value)
    except (RuntimeError, IOError) as exc:  # Replace with specific exceptions
        log_error(f"{MainAppLogMessages.SHUTDOWN_FAIL.value} {exc}")


# Register all routers
routes = [
    hello_routes,
    upload_route,
    to_chunks_route,
    chunks_to_embedding_routes,
    llm_settings_route,
    generate_routes,
    chat_manage_routes,
    monitor_router,
    logers_router,
    crawler_route,
    live_rag_route,
]
for router in routes:
    app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard page."""
    return templates.TemplateResponse("html/login.html", {"request": request})


@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    """Serve different pages based on the page_name parameter."""
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
        "chat_manager": "chat_manager.html",
    }

    template_name = allowed_pages.get(page_name)
    if not template_name:
        return templates.TemplateResponse(
            "html/404.html", {"request": request}, status_code=404
        )

    template_path = f"html/{template_name}" if template_name != "index.html" else template_name
    return templates.TemplateResponse(template_path, {"request": request})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(exc: RequestValidationError):
    """Handle request validation errors."""
    log_error(f"{MainAppLogMessages.VALIDATION_FAIL.value} {exc.errors()}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )
