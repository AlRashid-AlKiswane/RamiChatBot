# -*- coding: utf-8 -*-
import os
import sys
import tracemalloc

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from config import get_settings, Settings

except ImportError as ie:
    raise ImportError(f"ImportError in {__file__}: {ie}")

tracemalloc.start()

class ChatHistoryManager:
    """
    Manages and stores the chat history of a conversation using LangChain's ConversationBufferMemory.
    """

    def __init__(self):
        self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

    def add_user_message(self, message: str) -> None:
        """Adds a user message to the memory."""
        self.memory.chat_memory.add_user_message(message)

    def add_ai_message(self, message: str) -> None:
        """Adds an AI message to the memory."""
        self.memory.chat_memory.add_ai_message(message)

    def get_chat_history(self) -> list:
        """Returns the list of messages from the memory."""
        return self.memory.load_memory_variables({}).get("chat_history", [])

    def clear_chat_history(self) -> None:
        """Clears the memory history."""
        self.memory.chat_memory.clear()
        log_info("Chat history cleared.")

    def reset_memory(self) -> None:
        """Resets memory by reinitializing ConversationBufferMemory."""
        self.clear_chat_history()
        self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
        log_info("Memory has been reset.")

def main():
    chat_manager = ChatHistoryManager()
    chat_manager.add_user_message("Hello, how are you?")
    chat_manager.add_ai_message("I'm fine, thank you!")

    for message in chat_manager.get_chat_history():
        role = "User" if isinstance(message, HumanMessage) else "AI"
        print(f"{role}: {message.content}")

    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024:.2f} KB")
    print(f"Peak memory usage: {peak / 1024:.2f} KB")

    tracemalloc.stop()

if __name__ == "__main__":
    main()
