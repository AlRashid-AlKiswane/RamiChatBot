"""Routes package initialization.

This module imports and exposes all route modules for the application.
It serves as the central point for collecting all API routes.
"""

from .route_hello import hello_routes
from .route_doc_upload import upload_route
from .to_chunks import to_chunks_route
from .route_llm_settings import llm_settings_route
from .route_chat import generate_routes
from .route_histroy_mang import chat_manage_routes
from .route_embedd_chunks import chunks_to_embedding_routes
from .route_monitor import monitor_router
from .route_logs import logers_router
from .route_crawl import crawler_route
from .route_live_rag import live_rag_route
