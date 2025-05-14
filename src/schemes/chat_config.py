"""
Chat configuration schemas module.

This module defines Pydantic models for managing chat-related configurations,
including chat clearing and memory resetting functionality.
"""

from pydantic import BaseModel

class ChatManager(BaseModel):
    """Model for managing chat configuration settings.

    Attributes:
        clear_chat: Flag to indicate whether to clear the chat history (default: False)
        reset_memory: Flag to indicate whether to reset the conversation memory (default: False)
    """
    clear_chat: bool = False
    reset_memory: bool = False
