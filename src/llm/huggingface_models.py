import os
import sys
import torch
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

class HuggingFcaeModel(LLMsInterface):
    """
    Implementation of LLMsInterface for Hugging Face models (e.g., LLaMA).
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
        pad_token_id: int = None

    ) -> None:
        """
        Initialize tokenizer and model, with validated generation parameters.
        """
        try:
            try:
                
                login(get_settings().HUGGINGFACE_TOKIENS)
            except Exception as e:
                log_error(f"Failed to login to Hugging Face: {e}")
                raise RuntimeError(f"Hugging Face login failed: {e}")
            log_info(f"Initializing model: {model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code = trust_remote_code,

            )

            if top_k <= 0:
                raise ValueError("top_k must be a strictly positive integer.")

            self.generate_kwargs = {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "do_sample": do_sample,
            }

            # Optional: pad_token_id setup
            if pad_token_id is not None:
                self.generate_kwargs["pad_token_id"] = pad_token_id
            else:
                self.generate_kwargs["pad_token_id"] = self.tokenizer.eos_token_id

            log_info(f"Model {model_name} loaded with config: {self.generate_kwargs}")

        except Exception as e:
            log_error(f"Failed to load model {model_name}. Error: {e}")
            raise RuntimeError(f"Model initialization failed: {e}")

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

            full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = full_output[len(prompt):].strip()

            log_debug(f"Generated response: {response[:300]}...")

            return response

        except Exception as e:
            log_error(f"Error generating response. Prompt: {prompt[:60]}... Error: {e}")
            return "Error: Unable to generate response due to internal processing error."
