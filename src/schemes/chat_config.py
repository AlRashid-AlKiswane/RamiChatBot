from pydantic import BaseModel

class ChatManager(BaseModel):
    clear_chat: bool = False
    reset_memory: bool = False