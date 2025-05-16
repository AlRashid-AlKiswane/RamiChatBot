"""
Base LLM module: defines an abstract base class for language model interfaces.
"""

from abc import ABC, abstractmethod
from typing import Optional

# pylint: disable=too-many-arguments
class BaseLLM(ABC):
    """
    Abstract base class defining the interface for language model
    initialization and response generation.
    """

    @abstractmethod
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
    ) -> None:
        """
        Initialize the LLM with specific parameters.

        Args:
            model_name (str): The identifier of the language model.
            max_length (int): Maximum number of tokens to generate.
            temperature (float, optional): Sampling temperature.
            top_p (float, optional): Nucleus sampling probability threshold.
            top_k (int, optional): Top-K sampling cutoff.
            do_sample (bool, optional): Whether to sample randomly or use greedy decoding.
            trust_remote_code (bool, optional): Whether to trust remote code execution.
        """

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM given a prompt.

        Args:
            prompt (str): The input text prompt.

        Returns:
            str: The generated text response.
        """
