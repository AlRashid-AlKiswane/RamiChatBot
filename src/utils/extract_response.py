"""
Utility functions for extracting and processing LLM (Large Language Model) responses.

This module provides functions to clean and extract relevant portions from LLM outputs,
particularly when the response includes both the prompt and the answer.
"""

def extract_llm_answer_from_full(raw_output: str) -> str:
    """
    For LLM outputs that include the full prompt + response, 
    extract only the part that starts after the assistant marker.

    Args:
        raw_output: The complete output string from the LLM including prompt and response

    Returns:
        The extracted answer portion of the response, or the original string if no marker is found

    Example:
        >>> extract_llm_answer_from_full("Prompt... Answer: This is the response")
        "This is the response"
    """
    # This cuts everything before 'Answer:'
    try:
        return raw_output.split("Answer:")[-1].strip()
    except IndexError:
        return raw_output.strip()
