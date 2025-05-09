import unittest
from unittest.mock import MagicMock, patch, call
import sqlite3
import pandas as pd
import json

# Import the functions to test
from src.dbs import insert_chunk, insert_embedding, insert_query_response

class TestDatabaseInsertions(unittest.TestCase):
    def setUp(self):
        """Set up mock database connection and cursor for each test."""
        self.mock_conn = MagicMock(spec=sqlite3.Connection)
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    @patch('pandas.DataFrame.to_sql')
    def test_insert_chunk_success(self, mock_to_sql):
        """Test successful insertion of chunks."""
        # Create a sample DataFrame
        test_data = pd.DataFrame({
            'chunk_id': ['chunk1', 'chunk2'],
            'content': ['content1', 'content2'],
            'page_count': [1, 2],
            'pages': ['1', '1-2'],
            'sources': ['source1', 'source2'],
            'authors': ['author1', 'author2']
        })

        # Call the function
        insert_chunk(self.mock_conn, test_data)

        # Assert that to_sql was called with the correct parameters
        mock_to_sql.assert_called_once_with(
            "chunks", 
            self.mock_conn, 
            if_exists='append', 
            index=False
        )
        self.mock_conn.commit.assert_called_once()

    @patch('pandas.DataFrame.to_sql')
    def test_insert_chunk_failure(self, mock_to_sql):
        """Test handling of chunk insertion failure."""
        # Create a sample DataFrame
        test_data = pd.DataFrame({
            'chunk_id': ['chunk1'],
            'content': ['content1'],
            'page_count': [1],
            'pages': ['1'],
            'sources': ['source1'],
            'authors': ['author1']
        })

        # Simulate an error during insertion
        mock_to_sql.side_effect = Exception("DB error")

        # Call the function
        insert_chunk(self.mock_conn, test_data)

        # Verify rollback was called
        self.mock_conn.rollback.assert_called_once()

    def test_insert_embedding_success(self):
        """Test successful insertion of an embedding."""
        test_embedding = [0.1, 0.2, 0.3]
        test_chunk_id = "chunk123"

        # Call the function
        insert_embedding(self.mock_conn, test_embedding, test_chunk_id)

        # Verify the correct SQL was executed
        # Use call() to match the exact SQL string including whitespace
        expected_call = call("""
            INSERT INTO embeddings (chunk_id, embedding)
            VALUES (?, ?)
        """, (test_chunk_id, json.dumps(test_embedding)))
        
        self.mock_cursor.execute.assert_called_once()
        self.assertEqual(self.mock_cursor.execute.call_args, expected_call)
        self.mock_conn.commit.assert_called_once()

    def test_insert_embedding_failure(self):
        """Test handling of embedding insertion failure."""
        test_embedding = [0.1, 0.2, 0.3]
        test_chunk_id = "chunk123"

        # Simulate an error during insertion
        self.mock_cursor.execute.side_effect = Exception("DB error")

        # Call the function
        insert_embedding(self.mock_conn, test_embedding, test_chunk_id)

        # Verify rollback was called
        self.mock_conn.rollback.assert_called_once()

    def test_insert_query_response_success(self):
        """Test successful insertion of a query-response pair."""
        test_query = "What is AI?"
        test_response = "AI is artificial intelligence."
        test_user_id = "user123"

        # Call the function
        insert_query_response(self.mock_conn, test_query, test_response, test_user_id)

        # Verify the correct SQL was executed
        # Use call() to match the exact SQL string including whitespace
        expected_call = call("""
            INSERT INTO query_responses (user_id, query, response)
            VALUES (?, ?, ?)
        """, (test_user_id, test_query, test_response))
        
        self.mock_cursor.execute.assert_called_once()
        self.assertEqual(self.mock_cursor.execute.call_args, expected_call)
        self.mock_conn.commit.assert_called_once()

    def test_insert_query_response_validation_failure(self):
        """Test handling of invalid query-response data."""
        invalid_cases = [
            (123, "valid response", "user123"),  # invalid query (not string)
            ("valid query", 123, "user123"),    # invalid response (not string)
            ("valid query", "valid response", 123)  # invalid user_id (not string)
        ]

        for query, response, user_id in invalid_cases:
            with self.subTest(query=query, response=response, user_id=user_id):
                # Call the function with invalid data
                insert_query_response(self.mock_conn, query, response, user_id)
                
                # Verify no database operations were attempted
                self.mock_cursor.execute.assert_not_called()
                self.mock_conn.commit.assert_not_called()
                self.mock_conn.rollback.assert_not_called()

    def test_insert_query_response_db_failure(self):
        """Test handling of database failure during query-response insertion."""
        test_query = "What is AI?"
        test_response = "AI is artificial intelligence."
        test_user_id = "user123"

        # Simulate a database error
        self.mock_cursor.execute.side_effect = Exception("DB error")

        # Call the function
        insert_query_response(self.mock_conn, test_query, test_response, test_user_id)

        # Verify rollback was called
        self.mock_conn.rollback.assert_called_once()

if __name__ == '__main__':
    unittest.main()