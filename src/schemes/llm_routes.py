from typing import Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    model_name: str
    max_length: Optional[int] = 128
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    top_k: Optional[float] = 50.0
    do_sample: Optional[bool] = True
