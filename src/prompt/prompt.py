"""
Prompt builder for generating structured LLM prompts using Jinja2 templates.
Loads prompt templates from YAML files and renders them with user input,
context, and history.

Author: AlRashid AlKiswane
"""
import logging
import os
import sys
import yaml
from jinja2 import Template, TemplateError

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_debug, log_error, log_info

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

class PromptBuilder:
    """
    Builds prompts from YAML files using Jinja2 templating.
    """

    PROMPTS_DIR = os.path.join(MAIN_DIR, "prompt")  # Base directory for prompt files

    @staticmethod
    def load_prompt_file(filepath: str) -> str:
        """
        Loads and returns the raw prompt template string from a YAML file.

        :param filepath: Full path to the YAML file.
        :return: The raw Jinja2 template string for the prompt.
        :raises FileNotFoundError, ValueError, yaml.YAMLError: On failure.
        """
        try:
            log_debug(f"Loading prompt file: {filepath}")
            with open(filepath, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                prompt_template = data.get("prompt", "")
                if not prompt_template:
                    raise ValueError("Prompt field is missing or empty in YAML file.")
                log_info(f"Successfully loaded prompt from {filepath}")
                return prompt_template
        except FileNotFoundError:
            log_error(f"Prompt file not found: {filepath}")
            raise
        except yaml.YAMLError as yaml_err:
            log_error(f"YAML parsing error in {filepath}: {yaml_err}")
            raise
        except Exception as generic_err:
            log_error(f"Unexpected error loading prompt: {generic_err}")
            raise

    @staticmethod
    def build_prompt(prompt_name: str, user_message: str,
                     history: str = "", context: str = "") -> str:
        """
        Constructs and returns a structured prompt string using Jinja2 templating.

        :param prompt_name: Name of the YAML file (without `.yaml`).
        :param user_message: The latest message from the user.
        :param history: Previous conversation history.
        :param context: Additional context for the prompt.
        :return: Rendered prompt string.
        :raises TemplateError: On Jinja2 rendering failure.
        :raises Exception: For unexpected errors.
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

        except TemplateError as template_err:
            log_error(f"Template rendering error for '{prompt_name}': {template_err}")
            raise
        except Exception as generic_err:
            log_error(f"Unexpected error while building prompt: {generic_err}")
            raise


if __name__ == "__main__":
    log_info("Running prompt builder test...")
    test_prompt = PromptBuilder.build_prompt(
        prompt_name="rami_issa",
        user_message="Hi Rami, I'm AlRashid. What is 1 + 1?"
    )
    print("Generated Prompt:\n", test_prompt)
