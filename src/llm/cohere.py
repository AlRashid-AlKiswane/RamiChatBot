"""
cohere_llm.py

This module defines the `CohereLLM` class, which wraps the Cohere language model API.
"""

import os
import sys
import logging
from typing import Optional

import cohere

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info
    from src.helpers import get_settings, Settings
    from .base_llm import BaseLLM
    from src.enums import CohereLogMessages

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
    raise
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
    raise
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


class CohereLLM(BaseLLM):
    """
    A class that integrates the Cohere language model with a customizable interface.
    """

    def __init__(self):
        """
        Initializes the CohereLLM instance by loading application settings.
        """
        try:
            self.app_settings: Settings = get_settings()
        except Exception as e:
            log_error(CohereLogMessages.SETTINGS_LOAD_FAIL.value + f" Exception: {e}")
            raise RuntimeError(CohereLogMessages.SETTINGS_LOAD_FAIL.value) from e

    # pylint: disable= arguments-differ
    # pylint: disable= too-many-positional-arguments
    # pylint: disable= too-many-arguments
    # pylint: disable= attribute-defined-outside-init
    def initialize_llm(
        self,
        model_name: str,
        max_new_tokens: int,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 0.95,
        top_k: Optional[int] = 50
    ):
        """
        Configures the Cohere client and sets generation parameters.
        """
        try:
            api_key = self.app_settings.COHERE_API
            if not api_key:
                raise ValueError(CohereLogMessages.API_KEY_MISSING.value)

            self.co = cohere.Client(api_key)
            self.model_name = model_name
            self.max_new_tokens = max_new_tokens
            self.temperature = temperature
            self.top_p = top_p
            self.top_k = top_k

            log_info(CohereLogMessages.INIT_SUCCESS.value.format(model_name))
        except Exception as e:
            log_error(CohereLogMessages.INIT_FAIL.value + f" Exception: {e}")
            raise RuntimeError(CohereLogMessages.INIT_FAIL.value) from e

    def generate_response(self, prompt: str) -> str:
        """
        Generates a text response using the configured Cohere language model.
        """
        try:
            if not hasattr(self, 'co'):
                raise RuntimeError(CohereLogMessages.CLIENT_NOT_INITIALIZED.value)

            response = self.co.generate(
                model=self.model_name,
                prompt=prompt,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                p=self.top_p,
                k=self.top_k,
                stop_sequences=[],
                return_likelihoods='NONE'
            )

            return response.generations[0].text.strip()
        except Exception as e:
            log_error(CohereLogMessages.GENERATION_FAIL.value + f" Exception: {e}")
            raise RuntimeError(CohereLogMessages.GENERATION_FAIL.value) from e
