from typing import Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    model_name: str
    max_new_tokens: int 
    temperature: float 
    top_p: float
    top_k: int 
    trust_remote_code: bool 
    do_sample: bool 
    quantization: bool 
    quantization_type: str 
