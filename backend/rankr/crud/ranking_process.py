from pathlib import Path
from typing import Dict, List, Tuple, Union

from sqlalchemy import func
from sqlalchemy.orm import Session
from tqdm import tqdm

from config import dbc
from rankr import db_models as d
from rankr.crud.metrics_process import metrics_process
from utils import csv_size, fuzzy_matcher, get_row, nullify


def ranking_process(
    db: Session, file_path: Union[Path, str], soup: Dict[str, Dict[str, str]]
) -> Tuple[List[d.Institution], List[Dict[str, str]], List[Dict[str, str]]]:
    """Matches institutions with their GRID database counterparts.

    The functuin reads a .csv file row-by-row and for each row, tries
    to match the institution to a GRID ID, using various criteria. If
    that happens with success, the function will then assigns different
    metrics in the ranking to that institution object.

    Args:
        db (Session): SQLAlchemy session instant to connect to the DB
        file_path (Union[Path, str]): The path to the ranking .csv file
        soup (Dict[str, Dict[str, str]]): A set of choices for matching
        institutions

    Returns:
        Tuple[List[Institution], List[Dict[str, str]], List[Dict[str, str]]]:
        Three lists: matched institution, not-matched institutions, and
        institutions that were matched using the fuzzywuzzy library.
    """
    institutions_list: List[d.Institution] = []
    not_mached_list: List[Dict[str, str]] = []
    fuzz_list: List[Dict[str, str]] = []

    # useful queries:
    q1 = db.query(d.Institution)
    q2 = q1.join(d.Institution.country)

    rows = get_row(file_path)
    row_count = csv_size(file_path)

    pbar = tqdm(total=row_count)
    for row in rows:
        pbar.update()
        nullify(row)
        link_type = row["Ranking System"]
        inst_name = row["Institution"].strip().lower()
        inst_country = dbc.country_name_mapper(row["Country"])
        inst_url = row["URL"]

        inst_info = {
            "Raw": inst_name,
            "Country": inst_country,
            "URL": inst_url,
            "Ranking System": row["Ranking System"],
            "Ranking Type": row["Ranking Type"],
            "Year": row["Year"],
            "Field": row["Field"],
            "Subject": row["Subject"],
        }

        # checking link with institution links
        inst = (
            q1.join(d.Institution.links)
            .filter(d.Link.link == inst_url, d.Link.type == link_type)
            .first()
        )

        # checking grid_id in manual matches
        if not inst and inst_country in dbc.MATCHES:
            match = dbc.MATCHES[inst_country].get(inst_name)
            if match:
                inst = q1.filter(d.Institution.grid_id == match).first()

        # checking name with institution name
        if not inst:
            inst = q2.filter(
                func.lower(d.Institution.name) == inst_name,
                d.Country.country == inst_country,
            ).first()

        # fuzzy-mataching of strings
        if not inst:
            inst_grid_id = fuzzy_matcher(inst_name, inst_country, soup)
            if inst_grid_id:
                inst = q1.filter(d.Institution.grid_id == inst_grid_id).first()
                fuzz_list.append(
                    {"Fuzzy": inst.name, "GRID ID": inst_grid_id, **inst_info}
                )

        # could not match, or was matched before (with another institution)
        if not inst or inst in institutions_list:
            not_mached_list.append(
                {
                    "Problem": "Not Matched" if not inst else f"Double: {inst}",
                    **inst_info,
                }
            )
            continue

        ranking_metrics = metrics_process(row)
        inst_link_types = [link.type.name for link in inst.links]
        if (link_type not in inst_link_types) and inst_url:
            inst.links.append(d.Link(type=link_type, link=inst_url))
        inst.rankings.extend(ranking_metrics)
        institutions_list.append(inst)

    pbar.close()

    return (institutions_list, not_mached_list, fuzz_list)
