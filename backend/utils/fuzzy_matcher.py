import re

from fuzzywuzzy import fuzz, process


def fuzzy_matcher(
    inst_name: str,
    inst_country: str,
    soup: dict[str, dict[str, str]],
    education_rors: set[str] | None = None,
    score_cutoff: int = 100,
) -> str | None:
    """Selects the best-matching institution ROR id from a set of choices.

    Narrows choices by country, then scores them with fuzzywuzzy's
    `token_set_ratio`. Because `token_set_ratio` scores 100 on any *subset*
    match, a short/acronym query ("MIT") ties the real university (matched via
    its acronym in the soup) with verbose sub-units that merely contain the token
    ("Ragon Institute of MGH, MIT and Harvard"). We therefore collect *all*
    top-scoring candidates and break ties deterministically: prefer
    education-typed orgs, then the candidate whose name adds the fewest extra
    tokens, then the shortest name and so favoring the canonical university over
    its sub-units. Note this does NOT prefer parents, so UCLA is not pulled up
    to the "University of California System".

    'soup' is a dict like:

        {"country_1": {"University of Sydney | Australia | USYD | ...": "ror_id"}}

    Args:
        inst_name (str): The institution name to be matched.
        inst_country (str): The institution's country.
        soup (dict[str, dict[str, str]]): Candidate "soup string" -> ROR id,
            grouped by country.
        education_rors (set[str] | None): ROR ids typed "Education" in ROR, used
            only to break ties toward universities. Defaults to None.
        score_cutoff (int): Minimum token_set_ratio to accept. Defaults to 100.

    Returns:
        str | None: The ROR id of the best-matching institution.
    """
    if not inst_country:
        return None
    choices = soup.get(inst_country)
    if not choices:
        return None

    # "The University of Melbourne" -> "university of melbourne"
    inst_name = re.sub(r"^the\s", "", inst_name.lower(), count=1)
    query_tokens = set(inst_name.split())

    matches = process.extractBests(
        inst_name,
        choices.keys(),
        scorer=fuzz.token_set_ratio,
        score_cutoff=score_cutoff,
        limit=len(choices) or 1,
    )
    if not matches:
        return None

    top_score = matches[0][1]
    tied = [choice for choice, score in matches if score == top_score]
    if len(tied) == 1:
        return choices[tied[0]]

    def sort_key(choice: str) -> tuple[int, int, int]:
        is_education = bool(education_rors and choices[choice] in education_rors)
        name = choice.split("|", 1)[0].lower()
        extra_tokens = len(set(name.split()) - query_tokens)
        return (0 if is_education else 1, extra_tokens, len(name))

    return choices[min(tied, key=sort_key)]
