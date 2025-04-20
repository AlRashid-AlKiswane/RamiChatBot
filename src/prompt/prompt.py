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

# Prompt formatting constants
B_INST, E_INST = "[INST]", "[/INST]"
B_USER, E_USER = "<|USER|>", "<|END_USER|>"
B_ASSIST, E_ASSIST = "<|ASSIST|>", "<|END_ASSIST|>"
B_SYS, E_SYS = "<|SYSTEM|>", "<|END_SYSTEM|>"
B_SYS_INST, E_SYS_INST = "<|SYS_INST|>", "<|END_SYS_INST|>"

# Default system message
try:
    DEFAULT_SYSTEM_PROMPT = get_settings().DEFAULT_SYSTEM_PROMPT
except Exception as e:
    DEFAULT_SYSTEM_PROMPT = "You are RamiBot, a helpful assistant."
    log_error(f"Failed to load system prompt from settings. Using default: {e}")

class PromptBuilder:
    """
    Builds prompt templates for different models like LLaMA and Jais.
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

    def build_instruction_template(self) -> str:
        """
        Returns a structured instruction prompt with history and retrieved context.
        Optimized for clarity and LLM performance.
        """
        try:
            return (
                f"{B_INST}\n"
                f"<|HISTORY|>\n"
                f"{'{'}history{'}'}\n"
                f"<|END_HISTORY|>\n\n"
                f"<|RETRIEVED_CONTEXT|>\n"
                f"{'{'}retrieved_context{'}'}\n"
                f"<|END_RETRIEVED_CONTEXT|>\n\n"
                f"{B_USER}\n"
                f"{'{'}query{'}'}\n"
                f"{E_USER}\n\n"
                f"{B_ASSIST}\n"
                f"Respond in a clear, friendly, and helpful tone. Use any relevant information from the retrieved context and conversation history.\n\n"
                f"Rules:\n"
                f"- If the context is relevant, use it in your answer.\n"
                f"- If the context is unrelated, ignore it.\n"
                f"- If the answer is unknown, reply with “I don’t know.”\n"
                f"- Make sure your answer sounds natural and conversational.\n\n"
                f"[Response]:\n"
                f"{E_ASSIST}\n"
                f"{E_INST}"
            )
        except Exception as e:
            log_error(f"[build_instruction_template Error] {e}")
            raise


    def build_llama_prompt_template(self, system_message: str = DEFAULT_SYSTEM_PROMPT) -> str:
        """
        Constructs the full LLaMA-style instruction prompt with system message.
        """
        try:
            instruction = self.build_instruction_template()
            return f"{B_SYS}\n    {system_message}\n{E_SYS} \n{B_SYS_INST}\n{instruction}\n{E_SYS_INST}"
        except Exception as e:
            log_error(f"[build_llama_prompt_template Error] {e}")
            raise

    def get_prompt_template(self,
                            model_name: str,
                            system_message: str = DEFAULT_SYSTEM_PROMPT) -> Tuple[PromptTemplate, ConversationBufferMemory]:
        """
        Returns a PromptTemplate with query, history, and retrieved_context.
        """
        try:
            model_name = model_name.lower()
            if model_name not in ["llama", "jais"]:
                raise ValueError(f"Unsupported model name: {model_name}. Supported models: 'llama', 'jais'.")

            prompt_template = self.build_llama_prompt_template(system_message)

            prompt = PromptTemplate(
                input_variables=["query", "history", "retrieved_context"],
                template=prompt_template
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
    prompt, memory = prompt_builder.get_prompt_template("llama")
    history = memory.load_memory_variables({})["history"]

    formatted_prompt = prompt.format(
        query="What is the capital of France?",
        history=history,
        retrieved_context="France is a country in Europe. Paris is known as its capital."
    )
    print(formatted_prompt)
