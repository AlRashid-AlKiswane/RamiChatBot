import os
import sys
from typing import Tuple

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from config import get_settings, Settings

except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

# Default fallback system prompt
try:
    DEFAULT_SYSTEM_PROMPT = get_settings().DEFAULT_SYSTEM_PROMPT
except Exception as e:
    DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant."
    log_error(f"Failed to load system prompt from settings. Using default: {e}")


class PromptBuilder:
    """
    Builds clean, generic prompt templates suitable for any LLM.
    """

    def __init__(self):
        try:
            self.settings = get_settings()
            self.memory = ConversationBufferMemory(
                memory_key="history",
                return_messages=True,
                output_key="history"
            )
        except Exception as e:
            log_error(f"[PromptBuilder Init Error] {e}")
            raise

    def build_general_prompt_template(self, system_message: str) -> str:
        """
        Builds a general-purpose instruction prompt format.
        """
        try:
            return (
                f"{system_message}\n\n"
                f"Conversation History:\n"
                f"{{history}}\n\n"
                f"Relevant Context:\n"
                f"{{retrieved_context}}\n\n"
                f"User Question:\n"
                f"{{query}}\n\n"
                f"Assistant Response:"
            )
        except Exception as e:
            log_error(f"[build_general_prompt_template Error] {e}")
            raise

    def get_prompt_template(
        self,
        model_name: str = "generic",
        system_message: str = DEFAULT_SYSTEM_PROMPT
    ) -> Tuple[PromptTemplate, ConversationBufferMemory]:
        """
        Returns a PromptTemplate and memory buffer for any model.
        """
        try:
            template_str = self.build_general_prompt_template(system_message)
            prompt = PromptTemplate(
                input_variables=["query", "history", "retrieved_context"],
                template=template_str
            )
            log_debug(f"Prompt built for model: {model_name}")
            return prompt, self.memory
        except Exception as e:
            log_error(f"[get_prompt_template Error] {e}")
            raise
        finally:
            log_info(f"Prompt template for {model_name} generated successfully.")


if __name__ == "__main__":
    # Example usage
    prompt_builder = PromptBuilder()
    prompt, memory = prompt_builder.get_prompt_template("generic")

    history = memory.load_memory_variables({})["history"]

    formatted_prompt = prompt.format(
        query="What is the capital of France?",
        history=history,
        retrieved_context="France is a country in Western Europe. Paris is its capital."
    )

    print(formatted_prompt)
