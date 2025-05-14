# -*- coding: utf-8 -*-
import os
import sys
import yaml
from jinja2 import Template, TemplateError

MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(MAIN_DIR)

from logs import log_debug, log_error, log_info

class PromptBuilder:
    PROMPTS_DIR = f"{MAIN_DIR}/prompt"  # Base directory for prompt files

    @staticmethod
    def load_prompt_file(filepath: str) -> str:
        """
        Loads and returns the raw prompt template string from a YAML file.
        """
        try:
            log_debug(f"Loading prompt file: {filepath}")
            with open(filepath, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                prompt = data.get("prompt", "")
                if not prompt:
                    raise ValueError("Prompt field is missing or empty in YAML file.")
                log_info(f"Successfully loaded prompt from {filepath}")
                return prompt
        except FileNotFoundError:
            log_error(f"Prompt file not found: {filepath}")
            raise
        except yaml.YAMLError as e:
            log_error(f"YAML parsing error in {filepath}: {e}")
            raise
        except Exception as e:
            log_error(f"Unexpected error loading prompt: {e}")
            raise

    @staticmethod
    def build_prompt(prompt_name: str, user_message: str, history: str = "", context: str = "") -> str:
        """
        Constructs and returns a structured prompt string using Jinja2 templating.

        :param prompt_name: Name of the YAML file (without `.yaml`)
        :param user_message: The latest message from the user.
        :param history: Previous conversation history.
        :param context: Additional context for the prompt.
        :return: Rendered prompt string.
        """
        prompt_path = os.path.join(PromptBuilder.PROMPTS_DIR, "chat", f"{prompt_name}.yaml")
        try:
            template_str = PromptBuilder.load_prompt_file(prompt_path)
            log_debug("Rendering Jinja2 template...")

            template = Template(template_str)
            rendered_prompt = template.render(
                user_message=user_message or "",
                history=history or "",
                context=context or ""
            )

            log_info(f"Successfully built prompt for '{prompt_name}'")
            return rendered_prompt

        except TemplateError as e:
            log_error(f"Template rendering error for '{prompt_name}': {e}")
            raise
        except Exception as e:
            log_error(f"Unexpected error while building prompt: {e}")
            raise

# For direct testing
if __name__ == "__main__":
    try:
        log_info("Running prompt builder test...")
        prompt = PromptBuilder.build_prompt(
            prompt_name="rami_issa",
            user_message="Hi Rami, I'm AlRashid. What is 1 + 1?"
        )
        print("Generated Prompt:\n", prompt)
    except Exception as e:
        log_error(f"Error during prompt generation: {e}")


# prompt/chat/rami_issa.yaml
# prompt/chat/rami_issa.yaml