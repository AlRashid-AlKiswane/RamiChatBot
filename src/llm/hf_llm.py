"""
Hugging Face LLM loader and generator using transformers and optional quantization.
"""

import sys
from typing import Dict, Any, Optional

# pylint: disable=unused-import
import bitsandbytes

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

# Append root project directory to sys.path
try:
    from utils import setup_main_path
    MAIN_DIR = setup_main_path(levels_up=2)
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info, log_debug
    from src.helpers import get_settings, Settings

    from .base_llm import BaseLLM
except ImportError as ie:
    raise ImportError(f"ImportError in {__file__}: {ie}") from ie


class HuggingFaceLLM(BaseLLM):
    """
    Implementation of BaseLLM interface for Hugging Face models
    with optional quantization via bitsandbytes.
    """

    def __init__(self):
        self.app_settings: Settings = get_settings()
        self.model = None
        self.tokenizer = None
        self.generate_kwargs: Dict[str, Any] = {}

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
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
        Initialize tokenizer and model with validated generation parameters.
        Supports optional quantization using bitsandbytes.
        """
        try:
            login(self.app_settings.HUGGINGFACE_TOKIENS)
        except (torch.TorchRuntimeError, ValueError, RuntimeError) as e:
            log_error(f"Hugging Face login failed: {e}")
            raise RuntimeError(f"Hugging Face login failed: {e}") from e

        log_info(f"Initializing model: {model_name} (quantization={quantization})")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        model_kwargs = {
            "device_map": "auto",
            "trust_remote_code": trust_remote_code,
            "low_cpu_mem_usage": True,
            "torch_dtype": torch.float16,
        }

        if quantization:
            try:
                # Imported conditionally due to optional requirement
                if quantization_type == "8bit":
                    model_kwargs["load_in_8bit"] = True
                elif quantization_type == "4bit":
                    model_kwargs["load_in_4bit"] = True
                else:
                    raise ValueError("quantization_type must be '8bit' or '4bit'")
            except ImportError as imp_err:
                raise ImportError(
                    "Quantization requested but bitsandbytes is not installed."
                ) from imp_err

        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        except (torch.TorchRuntimeError, ValueError, RuntimeError) as e:
            log_error(f"Model loading failed for {model_name}: {e}")
            raise RuntimeError(f"Model initialization failed: {e}") from e

        if top_k <= 0:
            raise ValueError("top_k must be a strictly positive integer.")

        self.generate_kwargs = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.eos_token_id,
        }

        log_info(
            f"Model '{model_name}' initialized with settings: "
            f"{self.generate_kwargs}"
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generate text response from the model.
        """
        if not self.model or not self.tokenizer:
            log_error("Attempt to generate response before initializing model.")
            return "Error: Model is not initialized."

        try:
            log_debug(f"Generating response for prompt (preview): {prompt[:50]}...")

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            with torch.inference_mode():
                outputs = self.model.generate(**inputs, **self.generate_kwargs)

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            log_debug(f"Response generated (preview): {response[:300]}...")

            return response

        except (torch.TorchRuntimeError, ValueError, RuntimeError) as e:
            log_error(f"Generation failed for prompt: {prompt[:50]}... Error: {e}")
            return "Error: Internal error during response generation."
