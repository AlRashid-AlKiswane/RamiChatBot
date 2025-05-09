import unittest
import sqlite3
from unittest.mock import patch
from src.dbs import (
    create_chunks_table,
    create_embeddings_table,
    create_query_responses_table
)

class TestCreateTables(unittest.TestCase):

    def setUp(self):
        # Use in-memory SQLite DB
        self.conn = sqlite3.connect(":memory:")

    def tearDown(self):
        self.conn.close()

    @patch("src.logs.log_info")
    def test_create_chunks_table(self, mock_log_info):
        create_chunks_table(self.conn)
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks';")
        table = cursor.fetchone()
        self.assertIsNotNone(table)
        self.assertEqual(table[0], "chunks")

    @patch("src.logs.log_info")
    def test_create_embeddings_table(self, mock_log_info):
        # Must create chunks table first due to foreign key
        create_chunks_table(self.conn)
        create_embeddings_table(self.conn)
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings';")
        table = cursor.fetchone()
        self.assertIsNotNone(table)
        self.assertEqual(table[0], "embeddings")

    @patch("src.logs.log_info")
    def test_create_query_responses_table(self, mock_log_info):
        create_query_responses_table(self.conn)
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='query_responses';")
        table = cursor.fetchone()
        self.assertIsNotNone(table)
        self.assertEqual(table[0], "query_responses")

if __name__ == "__main__":
    unittest.main()
