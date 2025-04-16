from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChunkRequest(BaseModel):
    file_path: Optional[str] = None 

class Chunk(BaseModel):
    chunks: str
    metadata: Dict[str, Any]

class Embedding(BaseModel):
    chunk_id: int
    embedding: bytes

class QueryResponse(BaseModel):
    query: str
    response: str

