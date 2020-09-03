from typing import Dict, List

from tqdm import tqdm

from config import dbc
from rankr.db_models import (
    Acronym,
    Alias,
    Country,
    Institution,
    Label,
    Link,
    Type,
)
from utils import csv_size, get_csv, get_row, nullify


def institution_process(countries: Dict[str, Country]) -> List[Institution]:
    rows = get_row(dbc.GRID_DATABASE_DIR / "institutes.csv")
    row_count = csv_size(dbc.GRID_DATABASE_DIR / "institutes.csv")

    attrs = ["addresses", "acronyms", "aliases", "labels", "links", "types"]
    # Group the GRID data tables by grid_id for better access.
    institution_attrs = [
        get_csv(dbc.GRID_DATABASE_DIR / f"{attr}.csv", "grid_id")
        for attr in attrs
    ]

    institutions_list: List[Institution] = []
    pbar = tqdm(total=row_count)
    for row in rows:
        nullify(row)
        # Get all the data related to the current institution.
        address, acronym, alias, label, link, type = [
            attr.get(row["grid_id"]) for attr in institution_attrs
        ]

        # Create 'soup' variable for fuzzy matching of institutions.
        soup = [row["name"]]

        if address:
            country = dbc.country_name_mapper(address[0].pop("country"))
            institution = Institution(**{**row, **address[0]})
            institution.country = countries[country]
            soup.append(country)
        else:
            institution = Institution(**row)

        if acronym:
            institution.acronyms = [Acronym(**i) for i in acronym]
            soup.extend(i["acronym"] for i in acronym)
        if alias:
            institution.aliases = [Alias(**i) for i in alias]
            soup.extend(i["alias"] for i in alias)
        if label:
            institution.labels = [Label(**i) for i in label]
            soup.extend(i["label"] for i in label)
        if link:
            institution.links = [Link(**i) for i in link]
        if type:
            institution.types = [Type(**i) for i in type]

        institution.soup = " | ".join(i for i in soup)
        institutions_list.append(institution)

        pbar.update()
    pbar.close()
    del institution_attrs  # Free-up memory (~ 10^5 institutions).

    return institutions_list
