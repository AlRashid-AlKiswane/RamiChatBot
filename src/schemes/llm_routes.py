"""
LLM (Large Language Model) response configuration schemas.

This module defines Pydantic models for LLM response configurations,
including generation parameters and model specifications.
"""

from pydantic import BaseModel

class LLMResponse(BaseModel):
    """Configuration model for LLM response generation.

    Attributes:
        model_name: Name of the LLM model to use
        max_new_tokens: Maximum number of new tokens to generate
        temperature: Sampling temperature for generation
        top_p: Nucleus sampling probability threshold
        top_k: Number of highest probability tokens to consider
        trust_remote_code: Whether to trust remote code execution
        do_sample: Whether to use sampling in generation
        quantization: Whether to use quantized model
        quantization_type: Type of quantization to apply
    """
    model_name: str
    max_new_tokens: int
    temperature: float
    top_p: float
    top_k: int
    trust_remote_code: bool
    do_sample: bool
    quantization: bool
    quantization_type: str
