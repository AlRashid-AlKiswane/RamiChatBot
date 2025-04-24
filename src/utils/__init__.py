from .read_yaml import load_last_yaml
from .extract_response import extract_assistant_response

from llm import HuggingFcaeModel

model_hugging = HuggingFcaeModel()

model_hugging.init_llm()