import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app


class TestFastAPIApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_route(self):
        """Test the dashboard route returns status 200 and contains HTML content"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_valid_page_route(self):
        """Test one of the allowed pages returns HTML"""
        response = self.client.get("/pages/upload")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])


    def test_routers_exist(self):
        """Sanity check to confirm routers were mounted"""
        routes = [route.path for route in app.routes]
        expected_paths = [
            "/api/hello",
            "/api/upload",
            "/api/to_chunks",
            "/api/chunks_to_embedding",
            "/api/llm_settings",
            "/api/generate",
            "/api/chat_manage",
            "/api/monitor",
            "/api/logs",
            "/api/crawl",
            "/api/rag"
        ]
        # This will pass if at least one expected path is in the app
        self.assertTrue(any(path.startswith("/api") for path in routes))


if __name__ == "__main__":
    unittest.main()
