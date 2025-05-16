import os
import sys
import faiss
import numpy as np
# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info

except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")


def build_faiss_index(embedding: np.ndarray) -> faiss.IndexFlatL2:
    """
    Build a FAISS index from the given embedding.
    """
    try:
        log_info(f"[BUILD FAISS INDEX] Start building FAISS index.")
        dim = embedding.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embedding)
        return index
    except Exception as e:
        log_error(f"[BUILD FAISS INDEX ERROR] {e}")
        raise
