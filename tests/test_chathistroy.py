import unittest
from unittest.mock import patch, MagicMock
from langchain.schema import AIMessage, HumanMessage
from src.historys import ChatHistoryManager

class TestChatHistoryManager(unittest.TestCase):
    """Unit tests for the ChatHistoryManager class."""

    def setUp(self):
        """Set up a fresh ChatHistoryManager instance before each test."""
        self.chat_manager = ChatHistoryManager()
        self.user_id = "test_user"

    def test_add_user_message(self):
        """Test adding a user message to chat history."""
        message = "Hello, how are you?"
        self.chat_manager.add_user_message(self.user_id, message)
        history = self.chat_manager.get_chat_history(self.user_id)

        self.assertEqual(len(history), 1)
        self.assertIsInstance(history[0], HumanMessage)
        self.assertEqual(history[0].content, message)

    def test_add_ai_message(self):
        """Test adding an AI message to chat history."""
        message = "I'm doing well, thank you!"
        self.chat_manager.add_ai_message(self.user_id, message)
        history = self.chat_manager.get_chat_history(self.user_id)

        self.assertEqual(len(history), 1)
        self.assertIsInstance(history[0], AIMessage)
        self.assertEqual(history[0].content, message)

    def test_clear_chat_history(self):
        """Test clearing chat history."""
        self.chat_manager.add_user_message(self.user_id, "Hello!")
        self.chat_manager.clear_chat_history(self.user_id)
        history = self.chat_manager.get_chat_history(self.user_id)

        self.assertEqual(len(history), 0)

    def test_reset_memory(self):
        """Test resetting memory for a user."""
        self.chat_manager.add_user_message(self.user_id, "Hello!")
        self.chat_manager.reset_memory(self.user_id)
        history = self.chat_manager.get_chat_history(self.user_id)

        self.assertEqual(len(history), 0)

if __name__ == "__main__":
    unittest.main()
