from pydantic import BaseModel
from typing import List, Optional

class LlamaCPP(BaseModel):
    repo_id: str = "TheBloke/Llama-2-7b-Chat-GGUF"
    filename: str = "llama-2-7b-chat.Q2_K.gguf"
    n_ctx: int = 512
    n_threads: int = 4
    n_gpus: int = -1
    seed: int = 42
    verbose: bool = True
    max_new_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.95
    echo: bool = False
    stop: Optional[List[str]] = None
    model_name: str = "llama_cpp"  # Add if you want consistent naming with HuggingFace config