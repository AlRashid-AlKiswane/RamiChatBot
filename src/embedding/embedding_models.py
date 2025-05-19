

import logging
import os
import sys
from sentence_transformers import SentenceTransformer
from typing import Optional, Union

FILE_LOCATION = f"{os.path.dirname(__file__)}/sentence_model.py"

# Add root dir and handle potential import errors
try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)
    from src.logs import log_debug

    from logs import log_error, log_info
    from helpers import get_settings, Settings
except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


app_setting: Settings = get_settings()

class EmbeddingModel:
    """
    Handles SentenceTransformer-based embeddings.
    """
    def __init__(self):
        self.model_name = app_setting.EMBEDDING_MODEL
        try:
            self.model = SentenceTransformer(app_setting.EMBEDDING_MODEL)
            log_info(f"Embedding model '{app_setting.EMBEDDING_MODEL}' initialized.")
        except Exception as e:
            log_error(f"Failed to load embedding model '{app_setting.EMBEDDING_MODEL}': {e}")
            raise

    def embed(self, text: Union[str, list[str]], convert_to_tensor: bool = True, normalize_embeddings: bool = False) -> Optional[Union[list[float], list[list[float]]]]:
        """
        Generate embeddings for a given string or list of strings.
        """
        try:
            embedding = self.model.encode(text, convert_to_tensor=convert_to_tensor, normalize_embeddings=normalize_embeddings)
            preview_text = text if isinstance(text, str) else text[0]
            log_info(f"Generated embedding for text: {preview_text[:30]}...")
            return embedding
        except Exception as e:
            log_error(f"Error generating embedding: {e}")
            return None
        

if __name__ == "__main__":
    # Example usage
    embedding_model = EmbeddingModel()
    sample_text = "This is a test sentence."
    embedding = embedding_model.embed(sample_text)
    print(f"Embedding: {embedding}")