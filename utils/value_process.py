import re
from decimal import Decimal
from typing import Optional


def value_process(
    val: Optional[str], value_type: str = "integer"
) -> Optional[str]:
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
    val = re.search(range_pattern, val)
    try:
        lower_bound, upper_bound = val.groups()
        if upper_bound:
            val = (Decimal(lower_bound) + Decimal(upper_bound)) / 2
            val = str(int(val)) if value_type == "integer" else str(val)
            return val
        return lower_bound
    except AttributeError:
        return None
