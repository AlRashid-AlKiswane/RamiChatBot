"""
Chat history manager module.

Manages multi-user chat histories using LangChain's
ConversationBufferMemory. Includes logging and error handling.
"""

import os
import sys
import tracemalloc
from typing import Dict, List, Union

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

try:
    MAIN_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug

except ImportError as ie:
    print(f"Failed to import required modules: {ie}")
    raise ImportError(f"ImportError in {__file__}: {ie}") from ie


tracemalloc.start()


class ChatHistoryManager:
    """Manages and stores chat histories for multiple users."""

    def __init__(self) -> None:
        """Initialize the user memory dictionary."""
        self.user_memories: Dict[str, ConversationBufferMemory] = {}
        log_info("Multi-user ChatHistoryManager initialized.")

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """
        Retrieve or create memory buffer for a given user.

        Args:
            user_id: Unique user identifier.

        Returns:
            ConversationBufferMemory instance.
        """
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
            )
            log_debug(f"New memory initialized for user: {user_id}")
        return self.user_memories[user_id]

    def add_user_message(self, user_id: str, message: str) -> None:
        """
        Add a user message to the chat memory.

        Args:
            user_id: User identifier.
            message: User's message content.
        """
        try:
            self.get_memory(user_id).chat_memory.add_user_message(message)
            log_debug(f"[{user_id}] User message added: {message}")
        except AttributeError as err:
            log_error(
                f"[{user_id}] Failed to add user message due to attribute error: {err}"
            )
            raise

    def add_ai_message(self, user_id: str, message: str) -> None:
        """
        Add an AI message to the chat memory.

        Args:
            user_id: User identifier.
            message: AI's message content.
        """
        try:
            self.get_memory(user_id).chat_memory.add_ai_message(message)
            log_debug(f"[{user_id}] AI message added: {message}")
        except AttributeError as err:
            log_error(
                f"[{user_id}] Failed to add AI message due to attribute error: {err}"
            )
            raise

    def get_chat_history(
        self, user_id: str
    ) -> List[Union[HumanMessage, object]]:
        """
        Retrieve the chat history for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of messages in chat history.
        """
        try:
            memory = self.get_memory(user_id)
            history = memory.load_memory_variables({}).get("chat_history", [])
            log_debug(
                f"[{user_id}] Retrieved chat history with "
                f"{len(history)} messages."
            )
            return history
        except KeyError as err:
            log_error(f"[{user_id}] Chat history key error: {err}")
            return []

    def clear_chat_history(self, user_id: str) -> None:
        """
        Clear the chat history for a user.

        Args:
            user_id: User identifier.
        """
        try:
            memory = self.get_memory(user_id)
            memory.chat_memory.clear()
            log_info(f"[{user_id}] Chat history cleared.")
        except AttributeError as err:
            log_error(
                f"[{user_id}] Failed to clear chat history "
                f"due to attribute error: {err}"
            )
            raise

    def reset_memory(self, user_id: str) -> None:
        """
        Reset the conversation memory for a user.

        Args:
            user_id: User identifier.
        """
        self.user_memories[user_id] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
        )
        log_info(f"[{user_id}] Memory has been reset.")


def main() -> None:
    """
    Simple test runner for ChatHistoryManager simulating chat
    with two users and tracking memory usage.
    """
    chat_manager = ChatHistoryManager()

    # Simulate User A
    user_a = "user_a"
    chat_manager.add_user_message(user_a, "Hi, who are you?")
    chat_manager.add_ai_message(user_a, "I'm your assistant!")

    # Simulate User B
    user_b = "user_b"
    chat_manager.add_user_message(user_b, "Hello, what's the weather?")
    chat_manager.add_ai_message(user_b, "It's sunny today.")

    # Print chat history for both users
    for uid in (user_a, user_b):
        print(f"\n--- Chat History for {uid} ---")
        for message in chat_manager.get_chat_history(uid):
            role = "User" if isinstance(message, HumanMessage) else "AI"
            print(f"{role}: {message.content}")

    current, peak = tracemalloc.get_traced_memory()
    print(f"\nCurrent memory usage: {current / 1024:.2f} KB")
    print(f"Peak memory usage: {peak / 1024:.2f} KB")

    tracemalloc.stop()


if __name__ == "__main__":
    main()
