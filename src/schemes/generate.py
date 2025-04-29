from pydantic import BaseModel, Field, validator

class Generate(BaseModel):
    query: str = Field(..., min_length=1, max_length=2048, description="The user input query.")

    @validator('query')
    def strip_and_validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query must not be empty or whitespace only.")
        return value
