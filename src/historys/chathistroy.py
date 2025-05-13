# -*- coding: utf-8 -*-
import os
import sys
import tracemalloc
import traceback

from typing import Dict
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from helpers import get_settings, Settings

except ImportError as ie:
    print(f"Failed to import required modules: {ie}")
    raise ImportError(f"ImportError in {__file__}: {ie}")

tracemalloc.start()

class ChatHistoryManager:
    """
    Manages and stores chat histories for multiple users using LangChain's ConversationBufferMemory.
    """

    def __init__(self):
        try:
            self.user_memories: Dict[str, ConversationBufferMemory] = {}
            log_info("Multi-user ChatHistoryManager initialized.")
        except Exception as e:
            log_error(f"Error initializing ChatHistoryManager: {e}")
            raise

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
            log_debug(f"New memory initialized for user: {user_id}")
        return self.user_memories[user_id]

    def add_user_message(self, user_id: str, message: str) -> None:
        try:
            self.get_memory(user_id).chat_memory.add_user_message(message)
            log_debug(f"[{user_id}] User message added: {message}")
        except Exception as e:
            log_error(f"[{user_id}] Failed to add user message: {e}")
            raise

    def add_ai_message(self, user_id: str, message: str) -> None:
        try:
            self.get_memory(user_id).chat_memory.add_ai_message(message)
            log_debug(f"[{user_id}] AI message added: {message}")
        except Exception as e:
            log_error(f"[{user_id}] Failed to add AI message: {e}")
            raise

    def get_chat_history(self, user_id: str) -> list:
        try:
            memory = self.get_memory(user_id)
            history = memory.load_memory_variables({}).get("chat_history", [])
            log_debug(f"[{user_id}] Retrieved chat history with {len(history)} messages.")
            return history
        except Exception as e:
            log_error(f"[{user_id}] Failed to retrieve chat history: {e}")
            return []

    def clear_chat_history(self, user_id: str) -> None:
        try:
            memory = self.get_memory(user_id)
            memory.chat_memory.clear()
            log_info(f"[{user_id}] Chat history cleared.")
        except Exception as e:
            log_error(f"[{user_id}] Failed to clear chat history: {e}")
            raise

    def reset_memory(self, user_id: str) -> None:
        try:
            self.user_memories[user_id] = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
            log_info(f"[{user_id}] Memory has been reset.")
        except Exception as e:
            log_error(f"[{user_id}] Failed to reset memory: {e}")
            raise
    

def main():
    import tracemalloc
    import traceback

    try:
        tracemalloc.start()
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
        for uid in [user_a, user_b]:
            print(f"\n--- Chat History for {uid} ---")
            for message in chat_manager.get_chat_history(uid):
                role = "User" if isinstance(message, HumanMessage) else "AI"
                print(f"{role}: {message.content}")

        current, peak = tracemalloc.get_traced_memory()
        print(f"\nCurrent memory usage: {current / 1024:.2f} KB")
        print(f"Peak memory usage: {peak / 1024:.2f} KB")

    except Exception as e:
        log_error(f"An error occurred in main(): {e}\n{traceback.format_exc()}")
        print("An unexpected error occurred. See logs for more details.")
    finally:
        tracemalloc.stop()

if __name__ == "__main__":
    main()
