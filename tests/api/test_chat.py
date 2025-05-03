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

client = TestClient(app=app)

def test_chat_success():
    response = client.post("/chat?user_id=dx15?prompt_template_name=meta", json={"query": "Hello"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_chat_empty_query():
    response = client.post("/chat?user_id=dx15?prompt_template_name=meta", json={"query": ""})
    assert response.status_code == 400
