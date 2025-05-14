"""
Main FastAPI application entry point with authentication, routing, and startup configuration.
"""

import os
import sys
from datetime import timedelta
import logging

from fastapi import FastAPI, Form, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

# Path Setup
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.append(MAIN_DIR)

    from src.dbs import (
        create_chunks_table,
        create_embeddings_table,
        create_query_responses_table,
        create_sqlite_engine,
    )
    from src.embedding import EmbeddingModel
    from src.historys import ChatHistoryManager
    from src.auth import (
        ACCESS_TOKEN_EXPIRE_MINUTES,
        authenticate_user,
        create_access_token,
    )
    from src.logs import (
        log_error,
        log_info,
    )
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

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

# FastAPI Initialization
app = FastAPI()

# Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use with caution in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates Configuration
templates = Jinja2Templates(directory=os.path.join(MAIN_DIR, "src/web"))

# Constants
ALLOWED_PAGES = {
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

@app.on_event("startup")
async def startup_event():
    """Initialize application resources at startup."""
    log_info("[startup_event] Initializing FastAPI app.")
    try:
        app.state.conn = create_sqlite_engine()
        create_chunks_table(conn=app.state.conn)
        create_embeddings_table(conn=app.state.conn)
        create_query_responses_table(conn=app.state.conn)

        app.state.embedding_model = EmbeddingModel()
        app.state.llm = None  # Deferred loading of LLM
        app.state.chat_manager = ChatHistoryManager()
        app.state.RETRIEVAL_CONTEXT = "No relevant context found."

        log_info("[startup_event] Initialization completed successfully.")
    except (OSError, RuntimeError) as exc:
        log_error(f"[startup_event] Initialization failed: {exc}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources during application shutdown."""
    log_info("[shutdown_event] Shutting down FastAPI app.")
    conn = getattr(app.state, "conn", None)
    if conn:
        try:
            conn.close()
            log_info("[shutdown_event] SQLite connection closed.")
        except RuntimeError as exc:
            log_error(f"[shutdown_event] Error while closing resources: {exc}")

# Include All API Routes
for route in [
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
]:
    app.include_router(route, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Redirect to the login page when the root URL is accessed."""
    return templates.TemplateResponse("html/login.html", {"request": request})

@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    """Serve HTML pages based on the page name provided in the URL."""
    template_name = ALLOWED_PAGES.get(page_name)
    if not template_name:
        return templates.TemplateResponse(
            "html/404.html", {"request": request}, status_code=404
        )
    template_path = f"html/{template_name}" if template_name != "index.html" else template_name
    return templates.TemplateResponse(template_path, {"request": request})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """Handle request validation errors and return JSON response with details."""
    log_error(f"[validation_exception_handler] Validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page for user authentication."""
    return templates.TemplateResponse("html/login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle user login and set access token cookie."""
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "html/login.html",
            {"request": request, "error": "Invalid username or password"},
        )

    response = RedirectResponse(url="/pages/index", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {create_access_token(data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    log_info(f"[LOGIN] User '{username}' logged in successfully.")
    return response

@app.get("/logout")
async def logout():
    """Log out the user by deleting the access_token cookie."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
