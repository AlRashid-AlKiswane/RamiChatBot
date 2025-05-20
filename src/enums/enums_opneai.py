# openai_enums.py
"""
This module defines the OpenAILogEnums class, which contains enumerations
for log messages used in the openai_llm.py module. This helps in
standardizing log messages and making them easier to manage.
"""

from enum import Enum

# pylint: disable = line-too-long
class OpenAILogEnums(Enum):
    """
    Enumerations for log messages used in the OpenAI LLM integration.
    Each enum member represents a log message string, potentially with placeholders.
    """
    # ==========================================================================
    # OpenAILLM Class - __init__ (used with src.logs.log_error)
    # ==========================================================================
    INIT_SETTINGS_LOAD_FAILED = "Failed to load application settings in OpenAILLM: {error_message}"

    # ==========================================================================
    # OpenAILLM Class - initialize_llm (used with src.logs.log_error/log_info)
    # ==========================================================================
    # Note: The actual ValueError message "OpenAI API key is missing from settings."
    # is raised directly, then caught and logged using INIT_LLM_VALUE_ERROR.
    INIT_LLM_VALUE_ERROR = "ValueError during OpenAI LLM initialization: {error_message}"
    INIT_LLM_CLIENT_FAILED = "Failed to initialize OpenAI LLM client: {error_message}"
    INIT_LLM_SUCCESS = "OpenAI LLM initialized with model: {model_name}"
    INIT_LLM_PARAMS = "Generation parameters: max_tokens={max_tokens}, temperature={temperature}, top_p={top_p}"

    # ==========================================================================
    # OpenAILLM Class - generate_response (used with src.logs.log_error)
    # ==========================================================================
    # Note: RuntimeError messages like "OpenAI client is not initialized..." are raised directly.
    GEN_RESP_CONTENT_NONE = "OpenAI API response content is None." # No placeholders needed
    GEN_RESP_NO_CHOICES = "OpenAI API response did not contain expected choices or message. Response: {api_response}"
    GEN_RESP_TIMEOUT = "OpenAI API request timed out: {error_message}"
    GEN_RESP_RATE_LIMIT = "OpenAI API rate limit exceeded: {error_message}"
    GEN_RESP_API_ERROR = "OpenAI API returned an API Error: {error_object}" # For logging the error exception/object
    # The RuntimeError for APIError uses a specific format: f"OpenAI API error: {e.status_code} - {e.message}"
    # This can be constructed separately or added as another enum if needed for the exception string itself.
    GEN_RESP_FAILED = "Text generation failed with OpenAI LLM: {error_message}"

    # ==========================================================================
    # Example Usage (__main__ block in openai_llm.py) (used with logger.info/warning/error)
    # ==========================================================================
    MAIN_LOG_ATTEMPT_INIT = "Attempting to initialize OpenAILLM..."
    MAIN_LOG_INIT_SUCCESS = "OpenAILLM initialized successfully."
    MAIN_LOG_API_KEY_TEST_MISSING = "OPENAI_API_KEY_TEST environment variable is not set. Skipping example usage." # This is a warning
    MAIN_LOG_GENERATING_PROMPT = "Generating response for prompt: '{test_prompt}' with system message: '{system_message}'"
    MAIN_LOG_GENERATED_RESPONSE = "Generated response: {response_text}"
    MAIN_LOG_RUNTIME_ERROR = "Runtime error during example usage: {error_message}"
    MAIN_LOG_UNEXPECTED_ERROR = "An unexpected error occurred during example usage: {error_message}"


