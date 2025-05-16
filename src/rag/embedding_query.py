"""
embedding_query module for RAG: embed user queries into vector representations.
"""

from typing import List

from src.embedding import EmbeddingModel
from src.logs import log_error, log_info


def embed_query(
    query: str,
    embedder: EmbeddingModel,
    convert_to_tensor: bool = True,
    normalize_embeddings: bool = False,
) -> List[float]:
    """
    Embed a query using the provided embedder.

    Args:
        query: The text to be embedded.
        embedder: An instance of EmbeddingModel.
        convert_to_tensor: Whether to convert embeddings to a tensor.
        normalize_embeddings: Whether to apply normalization to embeddings.

    Returns:
        A list of floats representing the query embedding.
    """
    try:
        preview = query[:30] + "..." if len(query) > 30 else query
        log_info(f"[EMBED_QUERY] Starting embed for: {preview}")
        embedding = embedder.embed(
            query,
            convert_to_tensor=convert_to_tensor,
            normalize_embeddings=normalize_embeddings,
        )
        log_info("[EMBED_QUERY] Embed successful")
        # If the embedder returns a NumPy array or tensor, convert to list
        if hasattr(embedding, "tolist"):
            return embedding.tolist()  # type: ignore[attr-defined]
        return list(embedding)  # type: ignore
    except ImportError as imp_err:
        log_error(f"[EMBED_QUERY IMPORT ERROR] {imp_err}")
        raise ImportError(f"Failed to import dependencies in embed_query: {imp_err}") from imp_err
    except Exception as err:
        log_error(f"[EMBED_QUERY ERROR] {err}")
        raise ValueError(f"Error embedding query: {err}") from err
