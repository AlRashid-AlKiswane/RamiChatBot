"""
enums_deepseek_ai.py

This module defines enumerations for logging messages related to DeepSeek LLM operations.
These enums promote consistent and centralized logging throughout the DeepSeekLLM codebase.

Enum Classes:
    DeepSeekLogMessages: Contains log messages for each major operation and failure case.
"""

from enum import Enum


class DeepSeekLogMessages(Enum):
    """
    Enumeration of log messages used throughout the DeepSeekLLM integration.

    This enum centralizes all log messages related to initialization, configuration,
    and generation steps, helping maintain consistent and manageable logging practices.

    Attributes:
        INIT_START (str): Log message when DeepSeek initialization begins.
        INIT_SUCCESS (str): Log message upon successful initialization.
        INIT_FAILURE (str): Log message when initialization fails.
        SETTINGS_LOAD_FAILURE (str): Log message when application settings fail to load.
        API_KEY_MISSING (str): Log message for missing API key.
        GENERATION_START (str): Log message before response generation begins.
        GENERATION_SUCCESS (str): Log message upon successful generation.
        GENERATION_FAILURE (str): Log message when response generation fails.
        CLIENT_NOT_INITIALIZED (str): Log message when the client is used without being initialized.
    """
    # Initialization Logs
    INIT_START = "Initializing DeepSeek LLM with model: {model_name}"
    INIT_SUCCESS = "DeepSeek LLM successfully initialized with model: {model_name}"
    INIT_FAILURE = "Failed to initialize DeepSeek LLM: {error}"

    # Settings Error
    SETTINGS_LOAD_FAILURE = "Failed to load application settings: {error}"

    # API Key Error
    API_KEY_MISSING = "DeepSeek API key is missing."

    # Generation Logs
    GENERATION_START = "Generating response for prompt: {prompt}"
    GENERATION_SUCCESS = "Successfully generated response from DeepSeek."
    GENERATION_FAILURE = "Text generation failed: {error}"
    GENERATION_EXCEPTION = "Failed to generate response from DeepSeek"

    # Client Error
    CLIENT_NOT_INITIALIZED = "DeepSeek client is not initialized."
