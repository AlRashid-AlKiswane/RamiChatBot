import os
import sys
from fastapi import FastAPI
# Add the project's root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)


from api import endpoint_router, hello_router, upload_router

from motor.motor_asyncio import AsyncIOMotorClient
from src.utils.helpers import get_settings 

from pymongo import MongoClient

import logging
logging.getLogger('pymongo').setLevel(logging.WARNING)

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()


app.include_router(hello_router, prefix="/api/v1/hello", tags=["hello"])
app.include_router(upload_router, prefix="/api/v1/upload_documents", tags=["upload_documetns"])
app.include_router(endpoint_router, prefix="/api/v1/endpoint_chunks", tags=["process_endpoint"])
