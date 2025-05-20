"""
Chat history log message enums module.

Defines structured enum constants for log messages used in
the ChatHistoryManager module. This includes informational,
debug, and error message templates related to multi-user
chat history management operations.
"""

from enum import Enum


class ChatHistoryMessages(Enum):
    """
    Enumeration of log message templates used by the ChatHistoryManager.

    This enum provides a centralized set of message templates for
    consistent logging across chat history operations, including
    initialization, message additions, retrieval, clearing, resetting,
    and error reporting.

    Attributes:
        INIT_SUCCESS (str): Indicates successful initialization of the chat manager.
        NEW_MEMORY_INIT (str): Logs new memory initialization for a user.
        USER_MESSAGE_ADDED (str): Logs addition of a user message.
        AI_MESSAGE_ADDED (str): Logs addition of an AI message.
        CHAT_HISTORY_RETRIEVED (str): Logs retrieval of chat history with message count.
        CHAT_HISTORY_CLEARED (str): Logs clearing of a user's chat history.
        MEMORY_RESET (str): Logs resetting of a user's memory.

        ERROR_GET_MEMORY (str): Logs failure to get or initialize user memory.
        ERROR_ADD_USER_MESSAGE (str): Logs failure to add a user message.
        ERROR_ADD_AI_MESSAGE (str): Logs failure to add an AI message.
        ERROR_GET_CHAT_HISTORY (str): Logs failure to retrieve chat history.
        ERROR_CLEAR_CHAT_HISTORY (str): Logs failure to clear chat history.
        ERROR_RESET_MEMORY (str): Logs failure to reset user memory.
    """
    INIT_SUCCESS = "Multi-user ChatHistoryManager initialized."
    NEW_MEMORY_INIT = "New memory initialized for user: {}"
    USER_MESSAGE_ADDED = "[{}] User message added."
    AI_MESSAGE_ADDED = "[{}] AI message added."
    CHAT_HISTORY_RETRIEVED = "[{}] Retrieved chat history with {} messages."
    CHAT_HISTORY_CLEARED = "[{}] Chat history cleared."
    MEMORY_RESET = "[{}] Memory has been reset."

    # Error messages
    ERROR_GET_MEMORY = "Failed to get or initialize memory for user {}: {}"
    ERROR_ADD_USER_MESSAGE = "Failed to add user message for user {}: {}"
    ERROR_ADD_AI_MESSAGE = "Failed to add AI message for user {}: {}"
    ERROR_GET_CHAT_HISTORY = "Failed to retrieve chat history for user {}: {}"
    ERROR_CLEAR_CHAT_HISTORY = "Failed to clear chat history for user {}: {}"
    ERROR_RESET_MEMORY = "Failed to reset memory for user {}: {}"
