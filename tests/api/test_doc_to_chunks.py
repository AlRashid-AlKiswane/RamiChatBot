from fastapi.testclient import TestClient
import os
import sys
# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from src import app

except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")
client = TestClient(app)

def test_chunks_to_embedding_empty():
    response = client.post("/chunks_to_embedding", json={"text": ""})
    assert response.status_code in [400, 422]
