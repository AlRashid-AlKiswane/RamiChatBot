def extract_llm_answer_from_full(raw_output: str) -> str:
    """
    For LLM outputs that include the full prompt + response, 
    extract only the part that starts after the assistant marker.
    """
    # This cuts everything before 'Assistant: 💡'
    try:
        return raw_output.split("Assistant: 💡", 1)[1].strip()
    except IndexError:
        return raw_output.strip()
