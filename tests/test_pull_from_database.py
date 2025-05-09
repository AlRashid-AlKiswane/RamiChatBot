import unittest
from unittest.mock import MagicMock, patch
import sqlite3
from typing import List, Dict, Any, Tuple

# Import the function to test
from src.dbs import pull_from_table

class TestPullFromTable(unittest.TestCase):
    def setUp(self):
        """Set up mock database connection and cursor for each test."""
        self.mock_conn = MagicMock(spec=sqlite3.Connection)
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def test_cache_mode_found(self):
        """Test cache mode when response is found."""
        # Setup mock return value
        self.mock_cursor.fetchone.return_value = ("cached response",)
        
        # Test data
        cache_key = ("user123", "test query")
        
        # Call function
        result = pull_from_table(
            conn=self.mock_conn,
            table_name="any_table",
            rely_data="text",
            cach=cache_key
        )
        
        # Verify
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT response FROM query_responses WHERE user_id = ? AND query = ?",
            cache_key
        )
        self.assertEqual(result, "cached response")

    def test_cache_mode_not_found(self):
        """Test cache mode when response is not found."""
        # Setup mock return value
        self.mock_cursor.fetchone.return_value = None
        
        # Test data
        cache_key = ("user123", "test query")
        
        # Call function
        result = pull_from_table(
            conn=self.mock_conn,
            table_name="any_table",
            rely_data="text",
            cach=cache_key
        )
        
        # Verify
        self.assertIsNone(result)

    def test_general_fetch_mode(self):
        """Test general fetch mode with columns."""
        # Setup mock return value
        self.mock_cursor.fetchall.return_value = [
            ("text1", 1),
            ("text2", 2),
            ("text3", 3)
        ]
        
        # Call function
        result = pull_from_table(
            conn=self.mock_conn,
            table_name="test_table",
            rely_data="content",
            columns=["text", "id"]
        )
        
        # Verify
        expected = [
            {"id": 1, "content": "text1"},
            {"id": 2, "content": "text2"},
            {"id": 3, "content": "text3"}
        ]
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT text, id FROM test_table"
        )
        self.assertEqual(result, expected)

    def test_general_fetch_mode_empty_result(self):
        """Test general fetch mode with empty result."""
        # Setup mock return value
        self.mock_cursor.fetchall.return_value = []
        
        # Call function
        result = pull_from_table(
            conn=self.mock_conn,
            table_name="empty_table",
            rely_data="data",
            columns=["text", "id"]
        )
        
        # Verify
        self.assertEqual(result, [])

    def test_database_error_in_cache_mode(self):
        """Test error handling in cache mode."""
        # Setup mock to raise error
        self.mock_cursor.execute.side_effect = sqlite3.Error("DB error")
        
        # Call function
        result = pull_from_table(
            conn=self.mock_conn,
            table_name="any_table",
            rely_data="text",
            cach=("user1", "query1")
        )
        
        # Verify
        self.assertIsNone(result)

    def test_database_error_in_general_mode(self):
        """Test error handling in general fetch mode."""
        # Setup mock to raise error
        self.mock_cursor.execute.side_effect = sqlite3.Error("DB error")
        
        # Call function
        result = pull_from_table(
            conn=self.mock_conn,
            table_name="test_table",
            rely_data="text",
            columns=["col1", "col2"]
        )
        
        # Verify
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()