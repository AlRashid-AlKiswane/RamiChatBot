import os
import sys
from typing import Dict, Any, List, Optional
from llama_cpp import Llama
from huggingface_hub import login, hf_hub_download

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)

    from src.config import get_settings, Settings
    from src.logs import log_debug, log_error, log_info
    from src.llm.abstract_llms import AstracrtLLMs

except ImportError as ie:
    raise ImportError(f"ImportError in {__file__}: {ie}")


class LlamaCPP(AstracrtLLMs):
    """
    Implementation of LLMsInterface for Llama models using llama-cpp-python.
    """

    def __init__(self):
        self.llm = None
        self.generate_kwargs: Dict[str, Any] = {}

    def init_llm(
        self,
        repo_id: str = "TheBloke/Llama-2-7B-Chat-GGUF",
        filename: str = "llama-2-7b-chat.Q2_K.gguf",
        n_ctx: int = 128,
        n_threads: int = 4,
        seed: int = 42,
        n_gpus: int = -1,
        verbose: bool = True,
        max_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.95,
        echo: bool = False,
        stop: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize the Llama model with the specified parameters.
        """
        self.generate_kwargs = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "echo": echo,
        }
        if stop:
            self.generate_kwargs["stop"] = stop

        log_info(f"Initializing Llama model from: {repo_id}")
        try:
            token = get_settings().HUGGINGFACE_TOKIENS
            login(token)
            log_debug(f"Logged in to Hugging Face with token: {token[:10]}...")
        except Exception as e:
            log_error(f"Failed to login to Hugging Face: {e}")
            raise RuntimeError(f"Hugging Face login failed: {e}")

        try:
            local_model_path = hf_hub_download(repo_id=repo_id, filename=filename)
            self.llm = Llama(
                model_path=local_model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                seed=seed,
                verbose=verbose,
            )
            log_debug("Model loaded successfully.")
        except Exception as e:
            log_error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM given a prompt.
        """
        if self.llm is None:
            raise RuntimeError("Model not initialized. Call init_llm() first.")

        log_debug(f"Generating response for prompt: {prompt}")
        try:
            response = self.llm(prompt, **self.generate_kwargs)
            log_debug(f"Response generated successfully: {response}")
            return response["choices"][0]["text"]
        except Exception as e:
            log_error(f"Failed to generate response: {e}")
            raise RuntimeError(f"Response generation failed: {e}")


if __name__ == "__main__":
    llama_cpp = LlamaCPP()
    llama_cpp.init_llm()
    while True:
        query: str = str(input("Enter Your query or exit for quite: "))
        if query.lower() == "exit":
            break
        else:
            response = llama_cpp.generate_response(query)
            log_info(f"Generated Response: {response}")
