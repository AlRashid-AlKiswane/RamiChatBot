"""
Init file for LLM module. Exposes CPPLlaMa and HuggingFaceLLMs interfaces.
"""

from .hf_llm import HuggingFaceLLM
from .llama_cpp import CPPLlaMa
