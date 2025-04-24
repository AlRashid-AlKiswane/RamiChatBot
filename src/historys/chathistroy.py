# -*- coding: utf-8 -*-
import os
import sys
import tracemalloc
import traceback

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from config import get_settings, Settings

except ImportError as ie:
    print(f"Failed to import required modules: {ie}")
    raise ImportError(f"ImportError in {__file__}: {ie}")

tracemalloc.start()

class ChatHistoryManager:
    """
    Manages and stores the chat history of a conversation using LangChain's ConversationBufferMemory.
    """

    def __init__(self):
        try:
            self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
            log_info("ChatHistoryManager initialized.")
        except Exception as e:
            log_error(f"Error initializing memory: {e}")
            raise

    def add_user_message(self, message: str) -> None:
        try:
            self.memory.chat_memory.add_user_message(message)
            log_debug(f"User message added: {message}")
        except Exception as e:
            log_error(f"Failed to add user message: {e}")
            raise

    def add_ai_message(self, message: str) -> None:
        try:
            self.memory.chat_memory.add_ai_message(message)
            log_debug(f"AI message added: {message}")
        except Exception as e:
            log_error(f"Failed to add AI message: {e}")
            raise

    def get_chat_history(self) -> list:
        try:
            history = self.memory.load_memory_variables({}).get("chat_history", [])
            log_debug(f"Retrieved chat history with {len(history)} messages.")
            return history
        except Exception as e:
            log_error(f"Failed to retrieve chat history: {e}")
            return []

    def clear_chat_history(self) -> None:
        try:
            self.memory.chat_memory.clear()
            log_info("Chat history cleared.")
        except Exception as e:
            log_error(f"Failed to clear chat history: {e}")
            raise

    def reset_memory(self) -> None:
        try:
            self.clear_chat_history()
            self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
            log_info("Memory has been reset.")
        except Exception as e:
            log_error(f"Failed to reset memory: {e}")
            raise

def main():
    try:
        chat_manager = ChatHistoryManager()
        chat_manager.add_user_message("Hello, how are you?")
        chat_manager.add_ai_message("I'm fine, thank you!")

        for message in chat_manager.get_chat_history():
            try:
                role = "User" if isinstance(message, HumanMessage) else "AI"
                print(f"{role}: {message.content}")
            except Exception as e:
                log_error(f"Failed to print a message: {e}")

        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage: {current / 1024:.2f} KB")
        print(f"Peak memory usage: {peak / 1024:.2f} KB")

    except Exception as e:
        error_trace = traceback.format_exc()
        log_error(f"An error occurred in main(): {e}\n{error_trace}")
        print(f"An unexpected error occurred. See logs for more details.")

    finally:
        tracemalloc.stop()

if __name__ == "__main__":
    main()
