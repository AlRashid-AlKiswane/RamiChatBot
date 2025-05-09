import re

def extract_assistant_response(text: str) -> str:
    """
    Extracts the response between <|ASSIST|> and <|END_ASSIST|> tags.
    """
    texts = text.split("The answer:")
    if texts and len(texts) > 1:
        text = texts[1].split("<|END_ASSIST|>")[0].strip()  # Added strip() to clean up the response
    else:
        return "No assistant response found."
    return text
