import re

def extract_assistant_response(text: str) -> str:
    """
    Extracts the response between <|ASSIST|> and <|END_ASSIST|> tags.
    """
    match = re.search(r"<\|ASSIST\|>(.*?)<\|END_ASSIST\|>", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "No assistant response found."
