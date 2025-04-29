import os
import sys

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
    from embedding import EmbeddingModel
    from logs import log_error, log_info

except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")


def embed_query(query: str, embedder: EmbeddingModel, convert_to_tensor: bool = True, normalize_embeddings: bool = False) -> list:
    """
    Embed a query using the provided embedder.
    
    Args:
        query (str): The query to be embedded.
        embedder: The embedding model to use.

        convert_to_tensor (bool): Whether to convert the embeddings to a tensor.
        normalize_embeddings (bool): Whether to normalize the embeddings.
    Returns:
        list: The embedded query.
    """
    try:
        log_info(f"[EMBED QUERY] Embedding query: {query[:30]}...")  # Log the first 30 characters of the query
        # Embed the query
        query_embedding = embedder.embed(query, convert_to_tensor=convert_to_tensor, normalize_embeddings=normalize_embeddings)
        return query_embedding
    except Exception as e:
        log_error(f"[EMBED QUERY ERROR] {e}")
        raise ValueError(f"Error embedding query: {e}")