from pydantic import BaseModel

class Application(BaseModel):
    model_name: str 
    config_path: str