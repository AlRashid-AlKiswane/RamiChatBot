import unittest
from unittest.mock import patch, MagicMock
from src.controllers import WebsiteCrawler  # Adjust the import according to your actual file structure
import tempfile

class TestWebsiteCrawler(unittest.TestCase):

    @patch("requests.get")
    def test_crawl(self, mock_get):
        # Set up the mock to simulate a response for a URL
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><a href='/about'>About</a></html>"
        mock_get.return_value = mock_response

        # Instantiate WebsiteCrawler with a mock URL
        crawler = WebsiteCrawler(start_url="https://example.com", max_pages=2)

        # Run the crawl function
        visited_pages = crawler.crawl()

        # Assert that the crawl has visited the expected URLs
        self.assertIn("https://example.com", visited_pages)
        self.assertIn("https://example.com/about", visited_pages)
if __name__ == "__main__":
    unittest.main()