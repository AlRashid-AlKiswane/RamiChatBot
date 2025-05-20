"""
llm_types module.

Defines an enumeration for supported Large Language Model (LLM) types
used in the application. This enum standardizes references to different
LLM providers or implementations, facilitating consistent usage across
the codebase.
"""

from enum import Enum

class LLMType(str, Enum):
    """
    Enumeration of supported Large Language Model (LLM) types.

    Each member represents a distinct LLM provider or implementation
    supported by the application, useful for configuration, conditional
    logic, and ensuring consistent naming conventions.

    Members:
        HF (str): HuggingFace LLM.
        OPENAI (str): OpenAI's LLM services.
        GOOGLE (str): Google Generative AI LLM.
        COHERE (str): Cohere LLM API.
        DEEPSEEK (str): Deepseek AI LLM service.
    """

    HF = "HF"
    OPENAI = "openai"
    GOOGLE = "google"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"
