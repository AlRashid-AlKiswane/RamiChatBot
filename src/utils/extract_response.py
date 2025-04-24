import re

def extract_assistant_response(text: str) -> str:
    """
    Extracts the response between <|ASSIST|> and <|END_ASSIST|> tags.
    """
    texts = text.split("Answer:")
    if texts and len(texts) > 1:
        text = texts[1]
    else:
        return "No assistant response found."
    return text
