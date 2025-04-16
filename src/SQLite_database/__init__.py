from .create_sqlite_engin import create_sqlite_engine
from .create_taples import create_chunks_table, create_embeddings_table, create_query_responses_table
from .inset_to_database import insert_chunk, insert_embedding, insert_query_response

try:
    conn = create_sqlite_engine()
    create_chunks_table(conn=conn)
    create_embeddings_table(conn=conn)
    create_query_responses_table(conn=conn)
    
except Exception as e:
    print(f"Error in Create Taples in Database: {e}")