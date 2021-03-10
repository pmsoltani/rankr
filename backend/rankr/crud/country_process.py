from typing import List

from config import dbc
from rankr import db_models as d
from utils import get_row, nullify


def country_process() -> List[d.Country]:
    """Returns a list of Country objects to be stored in database."""
    rows = get_row(dbc.COUNTRIES_FILE)
    countries_list: List[d.Country] = []
    for row in rows:
        nullify(row)
        countries_list.append(d.Country(**row))

    return countries_list
