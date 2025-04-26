import os
import sys


FILE_LOCATION = f"{os.path.dirname(__file__)}/create_sqlite_engin.py"

# Add root dir and handle potential import errors
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
except Exception as e:
    msg = f"Import Error in: {FILE_LOCATION}, Error: {e}"
    raise ImportError(msg)


def pull_from_table(conn, table_name: str, columns: list = ["page_content", "id"]):
    """
    Pulls all data from a specified table in the SQLite database.

    Args:
        conn (sqlite3.Connection): The connection object to the SQLite database.
        table_name (str): The name of the table to pull data from.
        columns (list): The columns to select from the table. Default is ["page_content", "id"].

    Returns:
        list: A list of dictionaries representing the rows in the specified table.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = cursor.fetchall()
        log_info(f"Pulled {len(rows)} row(s) from '{table_name}' table.")

        # Corrected here: use 'rows', not 'chunks_data'
        chunks_as_dicts = [{"id": chunk_id, "text": chunk_text} for chunk_text, chunk_id in rows]

        return chunks_as_dicts
    except Exception as e:
        log_error(f"Error pulling data from '{table_name}' table: {e}")
        return []
    finally:
        log_debug(f"Successfully executed pull_from_table function.")


if __name__ == "__main__":
    # Example usage
    from create_sqlite_engin import create_sqlite_engine

    conn = create_sqlite_engine()
    table_name = "chunks"
    data = pull_from_table(conn, table_name, columns=["page_contest", "id"])
    print(f"Pulled data: {data}")