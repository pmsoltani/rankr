import re
from decimal import Decimal


def basic_process(text: str) -> str | None:
    if not text:
        return None
    return text.strip()


def text_process(text: str) -> str | None:
    if not text:
        return None
    parts = re.findall(r"[a-zA-Z0-9_.:/\&\(\)]+", text)
    return " ".join(parts)


def value_process(value: str | None, value_type: str = "integer") -> str | None:
    """Cleans and processes raw values to be stored in the database.

    Rank and score values from ranking tables can take many different shapes. Examples
    include values like: "250-300", " =9", "+1001", "800+", "1,532", "5%", "8 : 92", ...

    These will need to be converted into simple numeric forms, which is the purpose
    of this function.

    Args:
        value (str | None): The string to be processed
        value_type (str): The type of the final value. Defaults to "integer".

    Returns:
        str | None: [description]
    """
    if value is None:
        return None

    # Cleaning (e.g. " =9", "+1001", "800+", "1,532", "5%", "8 : 92", "ab134+=")
    clean_pattern = r"[\n\r\s\t\=\+\,\@\#\%a-zA-Z]"
    value = re.sub(clean_pattern, "", value)
    value_type = value_type.lower()

    if value_type == "percent" and ":" in value:
        # For "Female:Male Ratio" in THE ranking (e.g. "46:54" -> "46")
        return value.split(":")[0]

    # Dealing with ranges (e.g. Rank = "800-1000" -> "900", Rank = "47" -> "47")
    range_pattern = r"(\d+\.*\d*)[-־᠆‐‑‒–—―⁻₋−⸺⸻﹘﹣－:]*(\d+\.*\d*)*"
    matches = re.search(range_pattern, value)
    if matches is None:
        return None

    lower_bound, upper_bound = matches.groups()
    if upper_bound:  # e.g. Rank = "800-1000"
        total = (Decimal(lower_bound) + Decimal(upper_bound)) / 2
        return str(int(total)) if value_type == "integer" else str(total)

    return lower_bound  # e.g. Rank = "47"
