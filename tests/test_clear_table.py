import unittest
import sqlite3
from src.controllers import clear_table


class TestClearTable(unittest.TestCase):

    def setUp(self):
        """Set up in-memory DB and table."""
        self.conn = sqlite3.connect(":memory:")
        self.table_name = "test_table"
        self.create_table()

    def tearDown(self):
        """Close DB connection."""
        self.conn.close()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            CREATE TABLE {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """)
        cursor.executemany(f"INSERT INTO {self.table_name} (name) VALUES (?)", [("Alice",), ("Bob",)])
        self.conn.commit()
        cursor.close()

    def test_clear_valid_table(self):
        # Confirm we have data first
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        before = cursor.fetchone()[0]
        self.assertEqual(before, 2)

        # Now clear
        clear_table(self.conn, self.table_name)

        # Confirm table is empty
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        after = cursor.fetchone()[0]
        self.assertEqual(after, 0)

    def test_clear_invalid_table_name(self):
        with self.assertRaises(ValueError) as context:
            clear_table(self.conn, "drop students;")

        self.assertIn("Invalid table name", str(context.exception))


if __name__ == "__main__":
    unittest.main()
