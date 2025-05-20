"""
Chat history manager module.

Manages multi-user chat histories using LangChain's
ConversationBufferMemory. Includes memory management and
structured logging via enums. Provides methods to add user
and AI messages, retrieve, clear, and reset chat histories.
"""

import logging
import os
import sys
import tracemalloc
from typing import Dict, List, Union

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_info, log_debug, log_error
    from src.enums import ChatHistoryMessages

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
    raise
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
    raise
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


tracemalloc.start()


class ChatHistoryManager:
    """
    Manages and stores chat histories for multiple users using
    LangChain's ConversationBufferMemory.

    Methods allow adding user and AI messages, retrieving chat history,
    clearing chat history, and resetting memory per user.
    """

    def __init__(self) -> None:
        """
        Initialize the ChatHistoryManager with an empty dictionary
        to hold user-specific conversation memories.
        """
        try:
            self.user_memories: Dict[str, ConversationBufferMemory] = {}
            log_info(ChatHistoryMessages.INIT_SUCCESS.value)
        except Exception as e:
            log_error(f"Failed to initialize ChatHistoryManager: {e}")
            raise RuntimeError("ChatHistoryManager initialization failed.") from e

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """
        Retrieve the ConversationBufferMemory instance for a user,
        creating a new one if it does not exist.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            ConversationBufferMemory: Memory buffer for the user.

        Raises:
            RuntimeError: If memory cannot be retrieved or created.
        """
        try:
            if user_id not in self.user_memories:
                self.user_memories[user_id] = ConversationBufferMemory(
                    return_messages=True,
                    memory_key="chat_history",
                )
                log_debug(ChatHistoryMessages.NEW_MEMORY_INIT.value.format(user_id))
            return self.user_memories[user_id]
        except Exception as e:
            log_error(ChatHistoryMessages.ERROR_GET_MEMORY.value.format(user_id, e))
            raise RuntimeError(f"Could not get or initialize memory for user {user_id}") from e

    def add_user_message(self, user_id: str, message: str) -> None:
        """
        Add a user message to the specified user's chat memory.

        Args:
            user_id (str): User identifier.
            message (str): Message content from the user.

        Raises:
            RuntimeError: If adding the message fails.
        """
        try:
            self.get_memory(user_id).chat_memory.add_user_message(message)
            log_debug(ChatHistoryMessages.USER_MESSAGE_ADDED.value.format(user_id))
        except Exception as e:
            log_error(ChatHistoryMessages.ERROR_ADD_USER_MESSAGE.value.format(user_id, e))
            raise RuntimeError(f"Failed to add user message for user {user_id}") from e

    def add_ai_message(self, user_id: str, message: str) -> None:
        """
        Add an AI-generated message to the specified user's chat memory.

        Args:
            user_id (str): User identifier.
            message (str): Message content from the AI.

        Raises:
            RuntimeError: If adding the message fails.
        """
        try:
            self.get_memory(user_id).chat_memory.add_ai_message(message)
            log_debug(ChatHistoryMessages.AI_MESSAGE_ADDED.value.format(user_id))
        except Exception as e:
            log_error(ChatHistoryMessages.ERROR_ADD_AI_MESSAGE.value.format(user_id, e))
            raise RuntimeError(f"Failed to add AI message for user {user_id}") from e

    def get_chat_history(self, user_id: str) -> List[Union[HumanMessage, object]]:
        """
        Retrieve the full chat history for a user.

        Args:
            user_id (str): User identifier.

        Returns:
            List[Union[HumanMessage, object]]: List of messages in the chat history.

        Raises:
            RuntimeError: If chat history retrieval fails.
        """
        try:
            memory = self.get_memory(user_id)
            history = memory.load_memory_variables({}).get("chat_history", [])
            log_debug(ChatHistoryMessages.CHAT_HISTORY_RETRIEVED.value.format(user_id, len(history)))
            return history
        except Exception as e:
            log_error(ChatHistoryMessages.ERROR_GET_CHAT_HISTORY.value.format(user_id, e))
            raise RuntimeError(f"Failed to retrieve chat history for user {user_id}") from e

    def clear_chat_history(self, user_id: str) -> None:
        """
        Clear the chat history for the specified user.

        Args:
            user_id (str): User identifier.

        Raises:
            RuntimeError: If clearing chat history fails.
        """
        try:
            memory = self.get_memory(user_id)
            memory.chat_memory.clear()
            log_info(ChatHistoryMessages.CHAT_HISTORY_CLEARED.value.format(user_id))
        except Exception as e:
            log_error(ChatHistoryMessages.ERROR_CLEAR_CHAT_HISTORY.value.format(user_id, e))
            raise RuntimeError(f"Failed to clear chat history for user {user_id}") from e

    def reset_memory(self, user_id: str) -> None:
        """
        Reset the conversation memory for the specified user,
        replacing it with a new empty ConversationBufferMemory instance.

        Args:
            user_id (str): User identifier.

        Raises:
            RuntimeError: If resetting memory fails.
        """
        try:
            self.user_memories[user_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
            )
            log_info(ChatHistoryMessages.MEMORY_RESET.value.format(user_id))
        except Exception as e:
            log_error(ChatHistoryMessages.ERROR_RESET_MEMORY.value.format(user_id, e))
            raise RuntimeError(f"Failed to reset memory for user {user_id}") from e
