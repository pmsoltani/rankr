import re
from typing import Dict, Optional

from fuzzywuzzy import fuzz, process


def fuzzy_matcher(
    inst_name: str,
    inst_country: str,
    soup: Dict[str, Dict[str, str]],
    score_cutoff: int = 100,
) -> Optional[str]:
    """Selects the best matching institution from a set of choices.

    First the function narrows-down the list of choices by filtering
    the institution's country. It then uses the fuzzywuzzy library's
    token_set_ratio method to extract only 1 institution from 'soup'.

    'soup' if a dictionary like this:

    {
        "country_1": {"inst1": "grid_id1", "inst2": "grid_id1", ...}
        "country_2": {"inst3": "grid_id3", "inst4": "grid_id4", ...}
    }

    The keys of each country dictionary should have a format like this:

    "University of Sydney | Australia | USYD | Sydney University"

    which is a mix of institution's name, country, acroynms, labels and
    aliases.

    Args:
        inst_name (str): The institution name to be matched
        inst_country (str): The institution's country
        soup (Dict[str, Dict[str, str]]): A set of choices for matching
        the institution
        score_cutoff (int, optional): The accuracy of the algorithm.
        Defaults to 100.

    Returns:
        Optional[str]: The GRID ID of the best matching institution
    """
    if not inst_country:
        return None

    # "The University of Melbourne" -> "university of melbourne"
    inst_name = re.sub(r"^the\s", "", inst_name.lower(), count=1)

    inst_grid_id = process.extractOne(
        query=inst_name,
        choices=soup[inst_country].keys(),
        scorer=fuzz.token_set_ratio,
        score_cutoff=score_cutoff,
    )

    try:
        return soup[inst_country][inst_grid_id[0]]
    except TypeError:  # not a good enough match found
        return None
