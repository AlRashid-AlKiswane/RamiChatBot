"""
Llama.cpp configuration schemas module.

This module defines Pydantic models for configuring Llama.cpp parameters,
including model specifications, generation settings, and hardware configurations.
"""

from typing import List, Optional
from pydantic import BaseModel

class LlamaCPP(BaseModel):
    """Configuration model for Llama.cpp parameters.

    Attributes:
        repo_id: Hugging Face repository ID for the model (default: "TheBloke/Llama-2-7b-Chat-GGUF")
        filename: Model filename (default: "llama-2-7b-chat.Q2_K.gguf")
        n_ctx: Context window size in tokens (default: 512)
        n_threads: Number of CPU threads to use (default: 4)
        n_gpus: Number of GPUs to use (-1 for all) (default: -1)
        seed: Random seed (default: 42)
        verbose: Enable verbose output (default: True)
        max_tokens: Maximum tokens to generate (default: 128)
        temperature: Sampling temperature (default: 0.7)
        top_p: Nucleus sampling probability (default: 0.95)
        echo: Echo the prompt in the output (default: False)
        stop: List of stop sequences (default: None)
    """
    repo_id: str = "TheBloke/Llama-2-7b-Chat-GGUF"
    filename: str = "llama-2-7b-chat.Q2_K.gguf"
    n_ctx: int = 512
    n_threads: int = 4
    n_gpus: int = -1
    seed: int = 42
    verbose: bool = True
    max_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.95
    echo: bool = False
    stop: Optional[List[str]] = None
