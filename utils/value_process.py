import re
from decimal import Decimal
from typing import Optional


def value_process(
    val: Optional[str], value_type: str = "integer"
) -> Optional[str]:
    """Cleans and processes raw values to be stored in the database.

    Rank and score values from ranking tables can take many different
    shapes. Examples include values like: "250-300", " =9", "+1001",
    "800+", "1,532", "5%", "8 : 92", ...

    These will need to be converted into simple numeric forms, which is
    the purpose of this function.

    Args:
        val (Optional[str]): The string to be processed
        value_type (str, optional): The type of the final value.
        Defaults to "integer".

    Returns:
        Optional[str]: [description]
    """
    if val is None:
        return None

    # Cleaning (e.g. " =9", "+1001", "800+", "1,532", "5%", "8 : 92", "ab134+=")
    clean_pattern = r"[\n\r\s\t\=\+\,\@\#\%a-zA-Z]"
    val = re.sub(clean_pattern, "", val)
    value_type = value_type.lower()

    if value_type == "percent" and ":" in val:
        # For "Female:Male Ratio" in THE ranking (e.g. "46:54" -> "46")
        return val.split(":")[0]

    # Dealing with ranges (e.g. Rank = "800-1000" -> "900", Rank = "47" -> "47")
    range_pattern = r"(\d+\.*\d*)[-־᠆‐‑‒–—―⁻₋−⸺⸻﹘﹣－:]*(\d+\.*\d*)*"
    matches: Optional[re.Match[str]] = re.search(range_pattern, val)
    try:
        lower_bound, upper_bound = matches.groups()
        if upper_bound:  # e.g. Rank = "800-1000"
            total = (Decimal(lower_bound) + Decimal(upper_bound)) / 2
            val = str(int(total)) if value_type == "integer" else str(total)
            return val
        return lower_bound  # e.g. Rank = "47"
    except AttributeError:
        return None
