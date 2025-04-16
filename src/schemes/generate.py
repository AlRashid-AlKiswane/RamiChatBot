from pydantic import BaseModel


class Generate(BaseModel):
    query: str = "Write about your self."