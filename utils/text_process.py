import re


def text_process(text: str) -> str:
    """Cleans the input text for further processing.

    This function re-constructs the input string from the parts that
    match a pre-defined pattern. The pattern only allows for a small
    set of characters, making the output text free on unwanted string.

    Args:
        text (str): Input text

    Returns:
        str: Clean text
    """
    parts = re.findall(r"[a-zA-Z0-9_.:/\&\(\)]+", text)
    return " ".join(parts)
