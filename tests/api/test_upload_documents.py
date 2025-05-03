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

def test_upload_documents_empty():
    response = client.post("/upload/", json={"documents": []})
    assert response.status_code in {400, 422}
