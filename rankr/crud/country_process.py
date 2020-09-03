from typing import List

from config import dbc
from rankr.db_models import Country
from utils import get_row, nullify


def country_process() -> List[Country]:
    """Returns a list of Country objects to be stored in database."""
    rows = get_row(dbc.COUNTRIES_FILE)
    countries_list: List[Country] = []
    for row in rows:
        nullify(row)
        countries_list.append(Country(**row))

    return countries_list
