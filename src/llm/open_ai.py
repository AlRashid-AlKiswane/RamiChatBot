# openai_llm.py

"""
This module defines the `OpenAILLM` class, which provides an interface
for interacting with the OpenAI API. It extends a base LLM interface 
to support initialization, configuration, and text generation.

Classes:
    OpenAILLM: A wrapper class that initializes and 
    interacts with the OpenAI API to generate text.

Exceptions:
    Raises RuntimeError or ValueError with descriptive error messages for 
    configuration or generation failures.

Dependencies:
    - openai
    - src.logs (log_error, log_info)
    - src.helpers (get_settings, Settings)
    - base_llm (BaseLLM)
"""

import os
import sys
import logging
from typing import Optional, List, Dict

try:
    from openai import OpenAI, APIError, APITimeoutError, RateLimitError

    CURRENT_DIR = os.path.dirname(__file__)
    MAIN_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../"))

    if not os.path.exists(MAIN_DIR):
        MAIN_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
        if not os.path.exists(MAIN_DIR):
            raise FileNotFoundError("Project directory not found")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.helpers import get_settings, Settings
    from src.logs import log_error, log_info
    from src.enums import OpenAILogEnums  # Ensure this import is present and correct

    from .base_llm import BaseLLM

# pylint: disable = logging-format-interpolation
except ModuleNotFoundError as e:
    logging.error("ModuleNotFoundError: Required module not found - %e", e, exc_info=True)
    raise
except ImportError as e:
    logging.error("ImportError: Failed to import a module - %e", e, exc_info=True)
    raise
except FileNotFoundError as e:
    logging.error("FileNotFoundError: Required project directory not found - %e", e, exc_info=True)
    raise
except Exception as e:
    logging.critical("UnexpectedError: An unexpected error occurred - %e", e, exc_info=True)
    raise


class OpenAILLM(BaseLLM):
    """
    A class that integrates an OpenAI model with a customizable interface.
    
    Attributes:
        app_settings (Settings): Application-wide configuration including API keys.
        client (OpenAI): OpenAI API client instance.
        model_name (str): Name of the model to use for generation.
        max_tokens (int): Maximum number of tokens to generate.
        temperature (float): Controls the randomness of outputs.
        top_p (float): Cumulative probability for nucleus sampling.
        # OpenAI doesn't typically use top_k with chat completions in the same way,
        # but it can be a parameter for other endpoints or custom logic.
        # For simplicity, we'll focus on common chat completion parameters.
    """
    def __init__(self):
        """Initializes the OpenAILLM instance by loading application settings."""
        try:
            self.app_settings: Settings = get_settings()
            self.client: Optional[OpenAI] = None
            self.model_name: str = ""
            self.max_tokens: int = 1024
            self.temperature: Optional[float] = 0.7
            self.top_p: Optional[float] = 1.0
        except Exception as e:
            msg = OpenAILogEnums.INIT_SETTINGS_LOAD_FAILED.value.format(error_message=str(e))
            log_error(msg)
            raise RuntimeError(msg) from e

    # pylint: disable=too-many-arguments
    # pylint: disable=arguments-differ 
    # Disabling if BaseLLM.initialize_llm has a different signature
    def initialize_llm(
        self,
        model_name: str = "gpt-3.5-turbo",
        max_tokens: int = 1024,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 1.0,
    ):
        """
        Configures the OpenAI client and sets generation parameters.

        Args:
            model_name (str): The model identifier. Default "gpt-3.5-turbo".
            max_tokens (int): Max tokens to generate in the completion. Default 1024.
            temperature (float, optional): Sampling temperature. Default 0.7.
            top_p (float, optional): Nucleus sampling parameter. Default 1.0.
        
        Raises:
            ValueError: If the API key is missing.
            RuntimeError: If client initialization fails for other reasons.
        """
        try:
            api_key = self.app_settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OpenAI API key is missing from settings.")

            self.client = OpenAI(api_key=api_key)
            self.model_name = model_name
            self.max_tokens = max_tokens
            self.temperature = temperature
            self.top_p = top_p

            log_info(OpenAILogEnums.INIT_LLM_SUCCESS.value.format(model_name=model_name))
            log_info(OpenAILogEnums.INIT_LLM_PARAMS.value.format(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            ))

        except ValueError as ve:
            log_error(OpenAILogEnums.INIT_LLM_VALUE_ERROR.value.format(error_message=str(ve)))
            raise
        except Exception as e:
            msg = OpenAILogEnums.INIT_LLM_CLIENT_FAILED.value.format(error_message=str(e))
            log_error(msg)
            raise RuntimeError(msg) from e

    def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client is not initialized. Call initialize_llm first.")

        messages: List[Dict[str, str]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
            )

            if completion.choices and completion.choices[0].message:
                response_content = completion.choices[0].message.content
                # pylint: disable = no-else-return
                if response_content is not None:
                    return response_content.strip()
                else:
                    msg = OpenAILogEnums.GEN_RESP_CONTENT_NONE.value
                    log_error(msg)
                    raise RuntimeError(msg)
            else:
                msg = OpenAILogEnums.GEN_RESP_NO_CHOICES.value.format(api_response=completion)
                log_error(msg)
                raise RuntimeError()

        except APITimeoutError as e:
            msg = OpenAILogEnums.GEN_RESP_TIMEOUT.value.format(error_message=str(e))
            log_error(msg)
            raise RuntimeError(msg) from e
        except RateLimitError as e:
            msg = OpenAILogEnums.GEN_RESP_RATE_LIMIT.value.format(error_message=str(e))
            log_error(msg)
            raise RuntimeError(msg) from e
        except APIError as e:
            msg = OpenAILogEnums.GEN_RESP_API_ERROR.value.format(error_object=str(e))
            log_error(msg)
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = OpenAILogEnums.GEN_RESP_FAILED.value.format(error_message=str(e))
            log_error(msg)
            raise RuntimeError(msg) from e
