import time

import requests


ROR_AFFILIATION_URL = "https://api.ror.org/v2/organizations"
_SESSION = requests.Session()


def match_ror_affiliation(
    query: str,
    retries: int = 3,
    backoff: float = 2.0,
    timeout: float = 30.0,
) -> str | None:
    """Matches a raw affiliation string to a ROR id via ROR's affiliation API.

    ROR's affiliation matcher runs on the same data as our local DB but is tuned
    for messy affiliation strings, so it sidesteps the subset/acronym ties that
    trip up `token_set_ratio` (e.g. "MIT" -> a sub-unit that merely contains the
    token). Following ROR recommendations, we only return the match that ROR has
    marked as `chosen` (a better indicator of confidence than `score`) and leave
    everything else to the caller's fallback.

    Args:
        query (str): The affiliation string, e.g. "MIT, United States".
        retries (int): Attempts on HTTP 429 (rate limited). Defaults to 3.
        backoff (float): Base seconds between 429 retries (grows linearly).
        timeout (float): Per-request timeout in seconds.

    Returns:
        str | None: The ROR id of the chosen match, or None.
    """
    query = query.strip()
    if not query:
        return None

    for attempt in range(retries):
        try:
            resp = _SESSION.get(
                ROR_AFFILIATION_URL, params={"affiliation": query}, timeout=timeout
            )
        except requests.RequestException:
            return None

        if resp.status_code == 429:
            time.sleep(backoff * (attempt + 1))
            continue
        if not resp.ok:
            return None

        for item in resp.json().get("items", []):
            if item.get("chosen"):
                ror_url = item.get("organization", {}).get("id", "")
                return ror_url.rsplit("/", 1)[-1] or None
        return None

    return None
