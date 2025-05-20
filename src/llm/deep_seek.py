"""
deepseek_llm.py

This module defines the `DeepSeekLLM` class, which provides an interface
for interacting with the DeepSeek language model API. It extends a base LLM interface 
to support initialization, configuration, and text generation.

Classes:
    DeepSeekLLM: A wrapper class that initializes and 
    interacts with the DeepSeek API to generate text.

Exceptions:
    Raises RuntimeError or ValueError with descriptive error messages for 
    configuration or generation failures.

Dependencies:
    - openai (used for DeepSeek-compatible SDK)
    - src.logs (log_error, log_info)
    - src.helpers (get_settings, Settings)
    - base_llm (BaseLLM)
"""

import os
import sys
import logging
from typing import Optional

try:
    from openai import OpenAI

    # Append root project directory to sys.path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.helpers import get_settings, Settings
    from src.enums import DeepSeekLogMessages
    from .base_llm import BaseLLM

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
    raise
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
    raise
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


class DeepSeekLLM(BaseLLM):
    """
    A class that integrates the DeepSeek language model with a customizable interface.
    
    Attributes:
        app_settings (Settings): Application-wide configuration including API keys.
        client (OpenAI): DeepSeek-compatible OpenAI client instance.
        model_name (str): Name of the model to use for generation.
        max_new_tokens (int): Maximum number of tokens to generate.
        temperature (float): Controls the randomness of outputs.
        top_p (float): Cumulative probability for nucleus sampling.
        top_k (int): Number of top tokens to sample from.

    Methods:
        initialize_llm(model_name, max_new_tokens, temperature, top_p, top_k):
            Initializes the model configuration and authenticates the DeepSeek client.
        
        generate_response(prompt):
            Generates a text response for a given input prompt.
    """

    def __init__(self):
        """Initializes the DeepSeekLLM instance by loading application settings."""
        try:
            self.app_settings: Settings = get_settings()
        except Exception as e:
            log_error(f"{DeepSeekLogMessages.SETTINGS_LOAD_FAILURE.value}: {e}")
            raise RuntimeError(DeepSeekLogMessages.SETTINGS_LOAD_FAILURE.value) from e

    # pylint: disable= arguments-differ
    # pylint: disable= too-many-positional-arguments
    # pylint: disable= too-many-arguments
    # pylint: disable= attribute-defined-outside-init
    def initialize_llm(
        self,
        model_name: str = "deepseek-chat",
        max_new_tokens: int = 512,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 0.9,
        top_k: Optional[int] = 50
    ):
        """
        Configures the DeepSeek client and sets generation parameters.

        Args:
            model_name (str): The model identifier. Default "deepseek-chat".
            max_new_tokens (int): Max tokens to generate. Default 512.
            temperature (float): Sampling temperature. Default 0.7.
            top_p (float): Nucleus sampling parameter. Default 0.9.
            top_k (int): Top-k sampling parameter. Default 50.
        
        Raises:
            ValueError: If the API key is missing or invalid.
            Exception: If initialization fails.
        """
        try:
            api_key = self.app_settings.DEEPSEEK_API_KEY
            if not api_key:
                raise ValueError(DeepSeekLogMessages.API_KEY_MISSING.value)

            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            self.model_name = model_name
            self.max_new_tokens = max_new_tokens
            self.temperature = temperature
            self.top_p = top_p
            self.top_k = top_k

            log_info(DeepSeekLogMessages.INIT_SUCCESS.value.format(model_name))
        except Exception as e:
            log_error(f"{DeepSeekLogMessages.INIT_FAILURE.value}: {e}")
            raise

    def generate_response(self, prompt: str) -> str:
        """
        Generates a text response using the configured DeepSeek model.

        Args:
            prompt (str): The input string for generation.

        Returns:
            str: Generated text response.

        Raises:
            RuntimeError: If generation fails or model isn't initialized.
        """
        try:
            if not hasattr(self, 'client'):
                raise RuntimeError(DeepSeekLogMessages.CLIENT_NOT_INITIALIZED.value)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                stream=False
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            log_error(f"{DeepSeekLogMessages.GENERATION_FAILURE.value}: {e}")
            raise RuntimeError(DeepSeekLogMessages.GENERATION_EXCEPTION.value) from e
