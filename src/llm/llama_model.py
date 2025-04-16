import os
import sys
import torch # type: ignore
from typing import Dict, Any, Optional, List
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from config import get_settings, Settings
    from LLMsINTERFACE import LLMsInterface
except ImportError as ie:
    print(f"ImportError in {__file__}: {ie}")
    raise


class LlaMAModel(LLMsInterface):
    """
    Concrete implementation of the LLMsInterface for LLaMA-based models.
    Uses Hugging Face Transformers to load a model and generate responses.
    """

    def init_llm(
        self,
        model_name: str,
        max_length: int,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: float = 0.5,
        do_sample: bool = True
    ) -> None:
        """
        Initialize the model and tokenizer with generation parameters.
        """
        login(get_settings().HUGGINGFACE_TOKIENS)
        try:
            log_info(f"Initializing model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )

            self.generate_kwargs = {
                "max_length": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "do_sample": do_sample
            }

            log_info(f"Model {model_name} loaded successfully with generation config: {self.generate_kwargs}")

        except Exception as e:
            log_error(f"Failed to load model {model_name}. Error: {e}")
            raise

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the model based on a prompt.
        """
        try:
            log_debug(f"Generating response for prompt: {prompt[:60]}...")

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                output = self.model.generate(**inputs, **self.generate_kwargs)

            response = self.tokenizer.decode(output[0], skip_special_tokens=True)
            log_debug(f"Generated response: {response[:200]}...")

            return response

        except Exception as e:
            log_error(f"Error generating response. Prompt: {prompt[:60]}... Error: {e}")
            return "Error: Unable to generate response at this time."
