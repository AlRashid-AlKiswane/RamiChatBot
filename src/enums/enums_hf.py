"""
huggingface_log_enums.py

This module defines a standardized set of logging messages for the HuggingFaceLLM module.
The `HuggingFaceLogEnums` enumeration centralizes all key log statements used
throughout the Hugging Face LLM initialization, configuration, and generation pipeline.

Usage:
    Use these enums in the HuggingFaceLLM class to ensure consistent logging and error handling.
"""

from enum import Enum


class HuggingFaceLogEnums(Enum):
    """
    Enum for logging messages used in the Hugging Face LLM module.

    Each enum represents a specific log message related to initialization,
    configuration, generation, error handling, or runtime issues.
    """

    INIT_SETTINGS_LOAD_FAILED = "Failed to load Hugging Face settings: {error_message}"
    LOGIN_FAILED = "Hugging Face login failed: {error_message}"
    MODEL_INIT_SUCCESS = "Hugging Face model '{model_name}' initialized successfully."
    MODEL_INIT_PARAMS = (
        "Model generation parameters set: max_new_tokens={max_new_tokens}, "
        "temperature={temperature}, top_p={top_p}, top_k={top_k}, do_sample={do_sample}"
    )
    MODEL_LOADING_FAILED = "Model loading failed for '{model_name}': {error_message}"
    GENERATION_FAILED = "Response generation failed: {error_message}"
    GENERATION_SUCCESS = "Response generated successfully for prompt."
    MODEL_NOT_INITIALIZED = "Attempted to generate response before model initialization."
    INVALID_TOP_K = "top_k must be a strictly positive integer, but got: {top_k}"
    INVALID_QUANT_TYPE = (
        "Invalid quantization type '{quant_type}'. Must be '4bit' or '8bit'."
    )
    QUANT_NOT_INSTALLED = "Quantization requested but bitsandbytes is not installed."
    UNEXPECTED_ERROR = "Unexpected error during Hugging Face setup: {error_message}"
