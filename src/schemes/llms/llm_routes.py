from pydantic import BaseModel

class LLMResponse(BaseModel):
    """
    
    """
    model_name: str
    max_length: int
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: float = 0.5
    do_sample: bool = False