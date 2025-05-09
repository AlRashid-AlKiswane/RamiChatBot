import unittest
from unittest.mock import patch
from datetime import datetime
import os
import uuid
from src.controllers import get_clean_file_name  

class TestGetCleanFileName(unittest.TestCase):

    def test_empty_file_name(self):
        orig_file_name = ""
        result = get_clean_file_name(orig_file_name)
        self.assertTrue(result.startswith("file_"))


    def test_invalid_file_name_type(self):
        orig_file_name = None
        result = get_clean_file_name(orig_file_name)
        self.assertTrue(result.startswith("file_"))

    def test_missing_file_extension(self):
        orig_file_name = "file_without_extension"
        result = get_clean_file_name(orig_file_name)
        self.assertTrue(result.endswith(".dat"))

    def test_unique_filename_generation(self):
        orig_file_name = "sample.txt"
        result = get_clean_file_name(orig_file_name)
        self.assertTrue(result.startswith("sample_"))
        self.assertTrue(result.count("_") >= 2)  # Check for timestamp and UUID suffix



if __name__ == "__main__":
    unittest.main()