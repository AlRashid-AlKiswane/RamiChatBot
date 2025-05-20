"""
This module defines the `HuggingFaceLLM` class, which loads a Hugging Face
transformer model with optional quantization and generates text responses.

Classes:
    HuggingFaceLLM: Loads and interacts with Hugging Face models using transformers.

Exceptions:
    Raises RuntimeError or ValueError with clear error messages /
    for model loading or generation issues.

Dependencies:
    - torch
    - transformers
    - huggingface_hub
    - bitsandbytes (optional for quantization)
    - src.logs (log_error, log_info, log_debug)
    - src.helpers (get_settings, Settings)
    - base_llm (BaseLLM)
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

try:
    CURRENT_DIR = os.path.dirname(__file__)
    MAIN_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../"))

    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError("Project directory not found.")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.helpers import get_settings, Settings
    from src.logs import log_error, log_info, log_debug
    from src.enums import HuggingFaceLogEnums
    from .base_llm import BaseLLM

except ModuleNotFoundError as e:
    logging.error("ModuleNotFoundError: Required module not found - %s", e, exc_info=True)
    raise
except ImportError as e:
    logging.error("ImportError: Failed to import a module - %s", e, exc_info=True)
    raise
except FileNotFoundError as e:
    logging.error("FileNotFoundError: Required project directory not found - %s", e, exc_info=True)
    raise
except Exception as e:
    logging.critical("UnexpectedError: An unexpected error occurred - %s", e, exc_info=True)
    raise


class HuggingFaceLLM(BaseLLM):
    """
    A class that loads and manages Hugging Face transformer models with optional quantization.

    Attributes:
        app_settings (Settings): Configuration including Hugging Face token.
        model (AutoModelForCausalLM): Loaded Hugging Face model instance.
        tokenizer (AutoTokenizer): Tokenizer corresponding to the model.
        generate_kwargs (dict): Generation configuration parameters.
    """

    def __init__(self):
        """Initializes HuggingFaceLLM with app settings."""
        try:
            self.app_settings: Settings = get_settings()
            self.model = None
            self.tokenizer = None
            self.generate_kwargs: Dict[str, Any] = {}
        except Exception as e:
            msg = HuggingFaceLogEnums.INIT_SETTINGS_LOAD_FAILED.value.format(error_message=e)
            log_error(msg)
            raise RuntimeError(msg) from e

    def initialize_llm(
        self,
        model_name: str,
        max_new_tokens: int,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 0.95,
        top_k: Optional[int] = 50,
        do_sample: Optional[bool] = True,
        trust_remote_code: Optional[bool] = False,
        quantization: bool = False,
        quantization_type: str = "8bit"
    ) -> None:
        """
        Loads model and tokenizer from Hugging Face and applies generation config.

        Args:
            model_name (str): Model path or name from Hugging Face.
            max_new_tokens (int): Number of tokens to generate.
            temperature (float): Sampling temperature.
            top_p (float): Nucleus sampling parameter.
            top_k (int): Top-k filtering value.
            do_sample (bool): Whether to sample randomly.
            trust_remote_code (bool): Trust custom code in model.
            quantization (bool): Whether to use quantization.
            quantization_type (str): '4bit' or '8bit'.

        Raises:
            RuntimeError or ValueError on setup failure.
        """
        try:
            login(self.app_settings.HUGGINGFACE_TOKIENS)
        except Exception as e:
            msg = HuggingFaceLogEnums.LOGIN_FAILED.value.format(error_message=e)
            log_error(msg)
            raise RuntimeError(msg) from e

        log_info(f"Loading Hugging Face model: {model_name} (quantized={quantization})")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        except Exception as e:
            msg = HuggingFaceLogEnums.MODEL_LOADING_FAILED.value.format(
                model_name=model_name, error_message=e)
            log_error(msg)
            raise RuntimeError(msg) from e

        model_kwargs = {
            "device_map": "auto",
            "trust_remote_code": trust_remote_code,
            "low_cpu_mem_usage": True,
            "torch_dtype": torch.float16,
        }

        if quantization:
            if quantization_type == "8bit":
                model_kwargs["load_in_8bit"] = True
            elif quantization_type == "4bit":
                model_kwargs["load_in_4bit"] = True
            else:
                msg = HuggingFaceLogEnums.INVALID_QUANT_TYPE.value.format(
                    quant_type=quantization_type)
                raise ValueError(msg)

        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        except Exception as e:
            msg = HuggingFaceLogEnums.MODEL_LOADING_FAILED.value.format(
                model_name=model_name, error_message=e)
            log_error(msg)
            raise RuntimeError(msg) from e

        if top_k <= 0:
            msg = HuggingFaceLogEnums.INVALID_TOP_K.value.format(top_k=top_k)
            raise ValueError(msg)

        self.generate_kwargs = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.eos_token_id,
        }

        params_msg = HuggingFaceLogEnums.MODEL_INIT_PARAMS.value.format(
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            do_sample=do_sample,
        )
        log_debug(params_msg)

        init_msg = HuggingFaceLogEnums.MODEL_INIT_SUCCESS.value.format(model_name=model_name)
        log_info(init_msg)

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the loaded model given an input prompt.

        Args:
            prompt (str): The user input prompt.

        Returns:
            str: Generated model response.

        Raises:
            RuntimeError if generation fails.
        """
        if not self.model or not self.tokenizer:
            msg = HuggingFaceLogEnums.MODEL_NOT_INITIALIZED.value
            log_error(msg)
            raise RuntimeError(msg)

        try:
            log_debug(f"Generating response for prompt: {prompt[:50]}...")

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            with torch.inference_mode():
                outputs = self.model.generate(**inputs, **self.generate_kwargs)

            response: str = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            log_debug(
                (f"{HuggingFaceLogEnums.GENERATION_SUCCESS.value}"
                "Preview: {response[:300]}..."))
            return response.strip()

        except Exception as e:
            msg = HuggingFaceLogEnums.GENERATION_FAILED.value.format(error_message=e)
            log_error(msg)
            raise RuntimeError(msg) from e
