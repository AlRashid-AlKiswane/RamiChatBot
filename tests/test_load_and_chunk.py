import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path
from shutil import rmtree

MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(MAIN_DIR)

from src.controllers import load_and_chunk

class TestLoadAndChunk(unittest.TestCase):
    def setUp(self):
        # Create a temp directory and dummy PDF file
        self.temp_dir = tempfile.mkdtemp()
        self.temp_pdf_path = os.path.join(self.temp_dir, "file.pdf")
        with open(self.temp_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy content")

        # Patch settings used in load_and_chunk
        patcher = patch("src.config.get_settings")
        self.mock_get_settings = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_settings = MagicMock()
        self.mock_settings.DOC_LOCATION_SAVE = self.temp_dir
        self.mock_settings.FILE_ALLOWED_TYPES = [".pdf", ".txt"]
        self.mock_settings.FILE_DEFAULT_CHUNK_SIZE = 1000
        self.mock_settings.CHUNKS_OVERLAP = 200
        self.mock_get_settings.return_value = self.mock_settings

    def tearDown(self):
        rmtree(self.temp_dir)

    @patch("src.controllers.ConvetDocsToChunks.os.listdir", return_value=[])
    def test_no_files(self, mock_listdir):
        df = load_and_chunk()
        self.assertTrue(df.empty)

if __name__ == "__main__":
    unittest.main()
