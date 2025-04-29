from fastapi.testclient import TestClient
from src import app

client = TestClient(app)

def test_chat_success():
    response = client.post("/chat?user_id=test_user", json={"query": "Hello"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_chat_empty_query():
    response = client.post("/chat?user_id=test_user", json={"query": ""})
    assert response.status_code == 400
