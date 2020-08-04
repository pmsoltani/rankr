import re


def text_process(text: str) -> str:
    """Cleans the input text for further processing

    Args:
        text (str): Input text

    Returns:
        str: Clean text
    """
    parts = re.findall(r"[a-zA-Z0-9_.:/\&\(\)]+", text)
    return " ".join(parts)
