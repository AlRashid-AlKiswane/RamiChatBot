import os
import sys
from typing import Optional

from sentence_transformers import SentenceTransformer

# Set up main directory and imports
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from logs import log_error, log_info
except ImportError as ie:
    print(f"ImportError in {__file__}: {ie}")
    raise

def convet_chunks_to_embedding(text: str, embedding_model: SentenceTransformer) -> Optional[list[float]]:
    """
    Convert text into an embedding vector using the specified model.

    Args:
        text (str): The input text to embed.
        embedding_model (SentenceTransformer): The model used for embedding.

    Returns:
        Optional[list[float]]: The embedding vector, or None if an error occurs.
    """
    if not text:
        log_error("Input text is empty. Cannot generate embedding.")
        return None

    try:
        embedding = embedding_model.encode(text, convert_to_tensor=True)
        log_info(f"Generated embedding for text snippet: {text[:30]}...")
        return embedding
    except Exception as e:
        log_error(f"Error generating embedding for text: {e}")
        return None
