"""
embedding_query module for RAG: embed user queries into vector representations
using a pluggable embedding model interface.
"""

import logging
import os
import sys
import traceback
from typing import List

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.embedding import EmbeddingModel
    from src.enums.enums_embedding_query import EmbeddingQueryLogMessages

except (FileNotFoundError, OSError) as e:
    logging.error("Fatal error setting up project directory: %s", str(e))
    logging.error(traceback.format_exc())
    sys.exit(1)


def embed_query(
    query: str,
    embedder: EmbeddingModel,
    convert_to_tensor: bool = True,
    normalize_embeddings: bool = False,
) -> List[float]:
    """
    Embed a query string into a vector using the provided embedding model.

    Args:
        query (str): The query text to embed.
        embedder (EmbeddingModel): The embedding model instance.
        convert_to_tensor (bool): If True, return tensor format.
        normalize_embeddings (bool): If True, normalize the output embedding.

    Returns:
        List[float]: Vector representation of the embedded query.

    Raises:
        ImportError: If embedding dependencies are missing.
        ValueError: If embedding fails due to runtime or data issues.
    """
    try:
        preview = query[:30] + "..." if len(query) > 30 else query
        log_info(EmbeddingQueryLogMessages.INFO_STARTING_EMBED.value.format(preview))

        embedding = embedder.embed(
            query,
            convert_to_tensor=convert_to_tensor,
            normalize_embeddings=normalize_embeddings,
        )

        log_info(EmbeddingQueryLogMessages.INFO_EMBED_SUCCESS.value)

        if hasattr(embedding, "tolist"):
            return embedding.tolist()  # type: ignore[attr-defined]

        return list(embedding)  # type: ignore

    except ImportError as imp_err:
        log_error(EmbeddingQueryLogMessages.ERR_IMPORT_FAILURE.value.format(str(imp_err)))
        raise ImportError(EmbeddingQueryLogMessages.RAISE_IMPORT_ERROR.value.format(
            str(imp_err)
            )) from imp_err

    except Exception as err:
        log_error(EmbeddingQueryLogMessages.ERR_EMBEDDING_RUNTIME.value.format(str(err)))
        raise ValueError(EmbeddingQueryLogMessages.RAISE_VALUE_ERROR.value.format(
            str(err)
            )) from err
