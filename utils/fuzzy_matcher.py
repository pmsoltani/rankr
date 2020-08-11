from typing import Optional

from fuzzywuzzy import fuzz, process


def fuzzy_matcher(
    inst_name: str, inst_country: str, soup: dict, score_cutoff: int = 100,
) -> Optional[str]:
    inst_grid_id = process.extractOne(
        query=inst_name.lower(),
        choices=soup[inst_country].keys(),
        scorer=fuzz.token_set_ratio,
        score_cutoff=score_cutoff,
    )

    try:
        return soup[inst_country][inst_grid_id[0]]
    except TypeError:  # not a good enough match found
        return None
