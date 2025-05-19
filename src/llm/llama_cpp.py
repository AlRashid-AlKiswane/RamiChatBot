"""
Module for loading and using LLaMA models with llama-cpp-python.
"""

import logging
import os
import sys
from typing import Dict, Any
from huggingface_hub import login, hf_hub_download
from llama_cpp import Llama

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    sys.path.append(MAIN_DIR)
    sys.path.append(MAIN_DIR)

    from src.helpers import get_settings
    from src.logs import log_debug, log_error, log_info
    from .base_llm import BaseLLM

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise
class CPPLlaMa(BaseLLM):
    """
    Implementation of LLMsInterface for LLaMA models using llama-cpp-python.
    """

    def __init__(self):
        self.llm = None
        self.generate_kwargs: Dict[str, Any] = {}

    def init_llm(self, config: Dict[str, Any]) -> None:
        """
        Initialize the LLaMA model with provided configuration.

        Args:
            config (dict): Configuration options for model loading and generation.
        """
        self.generate_kwargs = {
            "max_tokens": config.get("max_tokens", 128),
            "temperature": config.get("temperature", 0.7),
            "top_p": config.get("top_p", 0.95),
            "echo": config.get("echo", False),
        }
        if config.get("stop"):
            self.generate_kwargs["stop"] = config["stop"]

        log_info(f"Initializing LLaMA model from: {config['repo_id']}")
        try:
            token = get_settings().HUGGINGFACE_TOKIENS
            login(token)
            log_debug(f"Logged in to Hugging Face with token: {token[:10]}...")
        except Exception as e:
            log_error(f"Failed to login to Hugging Face: {e}")
            raise RuntimeError(f"Hugging Face login failed: {e}") from e

        try:
            local_model_path = hf_hub_download(repo_id=config["repo_id"],
                                                filename=config["filename"])
            self.llm = Llama(
                model_path=local_model_path,
                n_ctx=config.get("n_ctx", 128),
                n_threads=config.get("n_threads", 4),
                seed=config.get("seed", 42),
                verbose=config.get("verbose", True),
            )
            log_debug("Model loaded successfully.")
        except Exception as e:
            log_error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}") from e

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM given a prompt.
        """
        if self.llm is None:
            raise RuntimeError("Model not initialized. Call init_llm() first.")

        log_debug(f"Generating response for prompt: {prompt}")
        try:
            result = self.llm(prompt, **self.generate_kwargs)
            log_debug(f"Response generated successfully: {result}")
            return result["choices"][0]["text"]
        except Exception as e:
            log_error(f"Failed to generate response: {e}")
            raise RuntimeError(f"Response generation failed: {e}") from e


if __name__ == "__main__":
    llama_cpp = CPPLlaMa()
    llama_cpp.init_llm({
        "repo_id": "TheBloke/Llama-2-7B-Chat-GGUF",
        "filename": "llama-2-7b-chat.Q2_K.gguf",
        "n_ctx": 128,
        "n_threads": 4,
        "seed": 42,
        "verbose": True,
        "max_tokens": 128,
        "temperature": 0.7,
        "top_p": 0.95,
        "echo": False,
        "stop": None,
    })

    while True:
        query = input("Enter your query or type 'exit' to quit: ").strip()
        if query.lower() == "exit":
            break

        generated = llama_cpp.generate_response(query)
        log_info(f"Generated Response: {generated}")
