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
B_ASSIST, E_ASSIST = "<|ASSISTANT|>", "<|END_ASSISTANT|>"
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

    Methods:
        - build_instruction_template: Constructs user instruction format.
        - build_llama_prompt_template: Full LLaMA-style prompt.
        - get_prompt_template: Returns PromptTemplate and memory object.
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

    def build_instruction_template(self, history_enabled: bool = True) -> str:
        """
        Builds the core user prompt with or without history.
        """
        try:
            if history_enabled:
                return (
                    f"{B_INST} {B_USER} {{user_message}} {E_USER} "
                    f"{B_ASSIST} {{assistant_message}} {E_ASSIST} {E_INST}"
                )
            else:
                return f"{B_INST} {B_USER} {{user_message}} {E_USER} {E_INST}"
        except Exception as e:
            log_error(f"[build_instruction_template Error] {e}")
            raise

    def build_llama_prompt_template(self, history_enabled: bool = True,
                                    system_message: str = DEFAULT_SYSTEM_PROMPT) -> str:
        """
        Constructs the full LLaMA-style instruction prompt.
        """
        try:
            instruction = self.build_instruction_template(history_enabled)
            return f"{B_SYS} {system_message} {E_SYS} {B_SYS_INST} {instruction} {E_SYS_INST}"
        except Exception as e:
            log_error(f"[build_llama_prompt_template Error] {e}")
            raise

    def get_prompt_template(self,
                            model_name: str,
                            history_enabled: bool = True,
                            system_message: str = DEFAULT_SYSTEM_PROMPT) -> Tuple[PromptTemplate, ConversationBufferMemory]:
        """
        Builds a PromptTemplate and memory for the specified model.

        Args:
            model_name (str): Name of the model ("llama", "jais").
            history_enabled (bool): Whether to include conversation history.
            system_message (str): Custom system prompt.

        Returns:
            Tuple[PromptTemplate, ConversationBufferMemory]
        """
        try:
            model_name = model_name.lower()
            if model_name not in ["llama", "jais"]:
                raise ValueError(f"Unsupported model name: {model_name}. Supported models: 'llama', 'jais'.")

            prompt_template = self.build_llama_prompt_template(history_enabled, system_message)

            input_vars = ["user_message"]
            if history_enabled:
                input_vars.append("assistant_message")

            prompt = PromptTemplate(
                input_variables=input_vars,
                template=prompt_template
            )

            log_debug(f"Prompt built for model: {model_name}, history_enabled: {history_enabled}")
            return prompt, self.memory

        except Exception as e:
            log_error(f"[get_prompt_template Error] {e}")
            raise
        finally:
            log_info(f"Prompt template for {model_name} generated successfully.")