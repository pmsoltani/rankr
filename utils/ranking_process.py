import re
from typing import Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session
from tqdm import tqdm

from config import DBConfig
from rankr.db_models import Country, Institution, Link
from utils import csv_size, fuzzy_matcher, get_row, metrics_process, nullify


def ranking_process(
    db: Session, file_path: str, soup: dict
) -> Tuple[List[Institution], List[Dict[str, str]]]:
    institutions_list = []
    not_mached_list = []
    fuzz_list = []

    # useful queries:
    q1 = db.query(Institution)
    q2 = q1.join(Institution.country)

    rows = get_row(file_path)
    row_count = csv_size(file_path)

    pbar = tqdm(total=row_count)
    for row in rows:
        pbar.update()
        nullify(row)
        link_type = row["Ranking System"]
        inst_name = row["Institution"].strip().lower()
        inst_country = DBConfig.country_name_mapper(row["Country"])
        inst_url = row["URL"]
        inst_acronym = re.search(r"\((.*?)\)$", inst_name)
        inst_bare_name = ""
        if inst_acronym:
            # institution acronym:
            # "universiti malaya (um)" -> "um"
            inst_acronym = inst_acronym.group(1).lower()
            # institution name without acronym:
            # "universiti malaya (um)" -> "universiti malaya"
            inst_bare_name = re.search(r"^(.*?)\(", inst_name)
            inst_bare_name = inst_bare_name.group(1).strip().lower()
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
        inst: Institution = q1.join(Institution.links).filter(
            Link.link == inst_url, Link.type == link_type
        ).first()

        # checking grid_id in manual matches
        if not inst and inst_country in DBConfig.MATCHES:
            match = DBConfig.MATCHES[inst_country].get(inst_name)
            if match:
                inst: Institution = q1.filter(
                    Institution.grid_id == match
                ).first()

        # checking name with institution name
        if not inst:
            inst: Institution = q2.filter(
                func.lower(Institution.name) == inst_name,
                Country.country == inst_country,
            ).first()

        # fuzzy-mataching of strings
        if not inst:
            inst_grid_id = fuzzy_matcher(inst_name, inst_country, soup)
            if inst_grid_id:
                inst: Institution = q1.filter(
                    Institution.grid_id == inst_grid_id
                ).first()
                fuzz_list.append(
                    {"Fuzzy": inst.name, "GRID ID": inst_grid_id, **inst_info}
                )

        # could not match, or matched before (with another institution)
        if not inst or inst in institutions_list:
            not_mached_list.append(
                {
                    "Problem": "Not Matched" if not inst else "Double Matched",
                    **inst_info,
                }
            )
            continue

        ranking_metrics = metrics_process(row)
        inst_link_types = [link.type.name for link in inst.links]
        if link_type not in inst_link_types and inst_url:
            inst.links.append(Link(type=link_type, link=inst_url))
        inst.rankings.extend(ranking_metrics)
        institutions_list.append(inst)

    pbar.close()

    return (institutions_list, not_mached_list, fuzz_list)
