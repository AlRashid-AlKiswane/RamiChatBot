"""
enums_google_ai.py

This module defines standardized logging messages for the GoogleLLM integration.
It uses Python's Enum class to group all logging message constants related to
initialization, response generation, error handling, and other operations 
in the `GoogleLLM` module.

By centralizing log strings, this approach enhances consistency, maintainability,
and simplifies localization or message updates across the codebase.
"""

from enum import Enum


class GoogleLLMLog(Enum):
    """
    Enum class for logging messages used throughout the GoogleLLM module.

    Each member of this Enum represents a log message for a specific
    operation or error scenario related to GoogleLLM initialization,
    response generation, and runtime behavior.
    """

    INITIALIZING = "Attempting to initialize GoogleLLM..."
    INITIALIZED_SUCCESSFULLY = "GoogleLLM initialized successfully."
    GENERATION_STARTED = "Generating response for prompt."
    GENERATED_RESPONSE = "Generated response."
    MODEL_NOT_INITIALIZED = (
        "Google LLM client (model or generation_config) is not initialized. "
        "Call initialize_llm first."
    )
    MISSING_API_KEY = "Google API key is missing from settings."
    INVALID_RESPONSE = "Google API response did not contain text."
    TEXT_GEN_FAILED = "Text generation failed with Google LLM."
    API_KEY_INVALID = "Google API key is not valid. Please check your configuration."
    INIT_SETTINGS_FAIL = "Failed to load application settings in GoogleLLM"
    INIT_FAILED = "Failed to initialize Google LLM"
    VALUE_ERROR_INIT = "ValueError during Google LLM initialization"
    RUNTIME_GEN_ERROR = "Failed to generate response from Google AI"
