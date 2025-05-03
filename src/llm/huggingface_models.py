# -*- coding: utf-8 -*-
import os
import sys
import torch
import bitsandbytes
from typing import Dict, Any
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from config import get_settings, Settings
    from .LLMsINTERFACE import LLMsInterface
except ImportError as ie:
    raise ImportError(f"ImportError in {__file__}: {ie}")

class HuggingFaceModel(LLMsInterface):
    """
    Implementation of LLMsInterface for Hugging Face models (e.g., LLaMA),
    with optional support for quantization using bitsandbytes.
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generate_kwargs: Dict[str, Any] = {}

    def init_llm(
        self,
        model_name: str,
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 50,
        trust_remote_code: bool = False,
        do_sample: bool = True,
        pad_token_id: int = None,
        quantization: bool = False,
        quantization_type: str = "8bit"  # Can be "8bit" or "4bit"
    ) -> None:
        """
        Initialize tokenizer and model with validated generation parameters.
        Supports optional quantization using bitsandbytes.
        """
        try:
            login(get_settings().HUGGINGFACE_TOKIENS)
        except Exception as e:
            log_error(f"Failed to login to Hugging Face: {e}")
            raise RuntimeError(f"Hugging Face login failed: {e}")

        log_info(f"Initializing model: {model_name} with quantization={quantization}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        model_kwargs = {
            "torch_dtype": torch.float16,
            "device_map": "auto",
            "trust_remote_code": trust_remote_code,
            "low_cpu_mem_usage": True,
            "device_map": "auto",
            "torch_dtype": "auto",  
        }

        if quantization:
            try:
                import bitsandbytes  # noqa: F401
                if quantization_type == "8bit":
                    model_kwargs["load_in_8bit"] = True
                elif quantization_type == "4bit":
                    model_kwargs["load_in_4bit"] = True
                else:
                    raise ValueError("quantization_type must be '8bit' or '4bit'")
            except ImportError:
                raise ImportError("Quantization requested but bitsandbytes is not installed.")

        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **model_kwargs
            )
        except Exception as e:
            log_error(f"Failed to load model {model_name}. Error: {e}")
            raise RuntimeError(f"Model initialization failed: {e}")

        if top_k <= 0:
            raise ValueError("top_k must be a strictly positive integer.")

        self.generate_kwargs = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "do_sample": do_sample,
        }

        # Setup pad_token_id
        self.generate_kwargs["pad_token_id"] = (
            pad_token_id if pad_token_id is not None else self.tokenizer.eos_token_id
        )

        log_info(f"Model {model_name} loaded with config: {self.generate_kwargs}")

    def generate_response(self, prompt: str) -> str:
        """
        Generate text response from the model.
        """
        if not self.model or not self.tokenizer:
            log_error("Model not initialized. Call `init_llm` first.")
            return "Error: Model is not initialized."

        try:
            log_debug(f"Generating response for prompt: {prompt[:60]}...")

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(**inputs, **self.generate_kwargs)

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            log_debug(f"Generated response: {response[:300]}...")

            return response

        except Exception as e:
            log_error(f"Error generating response. Prompt: {prompt[:60]}... Error: {e}")
            return "Error: Unable to generate response due to internal processing error."
