from typing import Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    model_name: str
    temperature: Optional[float] = 0.7
    max_new_tokens: Optional[int] = 128
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True
    trust_remote_code: Optional[bool] = False
