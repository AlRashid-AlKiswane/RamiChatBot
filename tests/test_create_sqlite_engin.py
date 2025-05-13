import unittest
import os
import sqlite3
from unittest.mock import patch, MagicMock
from src.dbs import create_sqlite_engine
from src.helpers import get_settings, Settings
app_setting: Settings = get_settings()

class TestCreateSQLiteEngine(unittest.TestCase):

    @patch("sqlite3.connect")
    def test_create_sqlite_engine_success(self, mock_connect):
        # Arrange
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Act
        conn = create_sqlite_engine()

        # Assert
        mock_connect.assert_called_once_with(database=app_setting.DATABASE_URL)
        self.assertEqual(conn, mock_conn)

    @patch.dict('os.environ', {
        'DATABASE_URL': 'sqlite:///test.db'
    }, clear=True)
    @patch("sqlite3.connect")
    def test_create_sqlite_engine_failure(self, mock_connect):
        # Clear settings cache so the patched env var is picked up
        get_settings.cache_clear()

        # Arrange
        mock_connect.side_effect = Exception("Failed to connect")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            create_sqlite_engine()
        self.assertEqual(str(context.exception), "Failed to connect")

    def tearDown(self):
        # Clean up test DB if created
        path = get_settings().DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(path):
            os.remove(path)

if __name__ == "__main__":
    unittest.main()
