"""
This module defines an enumeration class for standardized logging messages 
used in the Cohere language model integration. These messages facilitate 
consistent and clear logging throughout the application lifecycle related 
to the Cohere LLM client.

The `CohereLogMessages` enum includes messages for:
- Configuration loading errors
- Initialization status
- Missing API key
- Text generation failures
- Client initialization state
"""

from enum import Enum


class CohereLogMessages(Enum):
    """
    Enum class representing log messages specific to Cohere LLM operations.

    Attributes:
        SETTINGS_LOAD_FAIL (str): Message indicating failure to load application settings.
        INIT_SUCCESS (str): Message indicating successful initialization of the Cohere LLM 
            with a placeholder for the model name.
        INIT_FAIL (str): Message indicating failure to initialize the Cohere LLM.
        API_KEY_MISSING (str): Message indicating the Cohere API key is missing.
        GENERATION_FAIL (str): Message indicating failure during text generation using Cohere.
        CLIENT_NOT_INITIALIZED (str): Message indicating that the Cohere client has not been 
        initialized.
    """
    SETTINGS_LOAD_FAIL = "Failed to load application settings."
    INIT_SUCCESS = "Cohere LLM initialized successfully with model: {}"
    INIT_FAIL = "Failed to initialize Cohere LLM."
    API_KEY_MISSING = "Cohere API key is missing."
    GENERATION_FAIL = "Text generation failed using Cohere."
    CLIENT_NOT_INITIALIZED = "Cohere client is not initialized."
