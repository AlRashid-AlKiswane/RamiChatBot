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

def test_get_llm_config():
    response = client.get("/llms_config")
    assert response.status_code == 200
    assert "llm_name" in response.json()
