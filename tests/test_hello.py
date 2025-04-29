from fastapi.testclient import TestClient
from src import app

client = TestClient(app)

def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert "Hello" in response.text or "success" in response.text
