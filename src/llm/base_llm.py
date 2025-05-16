from abc import ABC, abstractmethod


class AstracrtLLMs(ABC):
    """
    Abstract base class that defines a standard interface for 
    initializing and generating responses from language models.
    """

    @abstractmethod
    def initilize_llm(
        self,
        model_name: str,
        max_length: int,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: float = 0.5,
        do_sample: bool = True,
        trust_remote_code: bool = False
    ) -> None:
        """
        Initialize the LLM with specific parameters.

        Args:
            model_name (str): The identifier of the language model.
            max_length (int): Maximum number of tokens to generate.
            temperature (float): Sampling temperature.
            top_p (float): Nucleus sampling probability threshold.
            top_k (float): Top-K sampling cutoff.
            do_sample (bool): Whether to sample randomly or use greedy decoding.
            trust_remote_code (bool): Whether to trust remote code execution.
        """
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM given a prompt.

        Args:
            prompt (str): The input text prompt.

        Returns:
            str: The generated text response.
        """
        pass
