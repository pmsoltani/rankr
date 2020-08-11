import re
from typing import Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session
from tqdm import tqdm

from config import DBConfig
from rankr.db_models import Acronym, Alias, Country, Institution, Link
from utils import csv_size, fuzzy_matcher, get_row, metrics_process, nullify


def ranking_process(
    db: Session, file_path: str, soup: dict
) -> Tuple[List[Institution], List[Dict[str, str]]]:
    institutions_list = []
    not_mached_list = []

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
        inst_name = row["Institution"].lower()
        inst_country = row["Country"]
        if inst_country == "Hong Kong":
            # The GRID database lists institutions in 'Hong Kong' as Chinese
            inst_country = "China"
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

        # checking link with institution links
        inst: Institution = q1.join(Institution.links).filter(
            Link.link == inst_url, Link.type == link_type
        ).first()

        # checking grid_id in manual matches
        if not inst and DBConfig.MATCHES.get(inst_name):
            inst: Institution = q1.filter(
                Institution.grid_id == DBConfig.MATCHES[inst_name]
            ).first()

        # checking name with institution name
        if not inst:
            inst: Institution = q2.filter(
                func.lower(Institution.name) == inst_name,
                Country.country == inst_country,
            ).first()

        if not inst:
            inst_grid_id = fuzzy_matcher(inst_name, inst_country, soup)
            if inst_grid_id:
                inst: Institution = q1.filter(
                    Institution.grid_id == inst_grid_id
                ).first()
                print(inst.name, "|", inst_name)

        # checking name with institution acronyms
        if not inst:
            inst: Institution = q2.join(Institution.acronyms).filter(
                func.lower(Acronym.acronym) == inst_name,
                Country.country == inst_country,
            ).first()

        # checking name with institution aliases
        if not inst:
            inst: Institution = q2.join(Institution.aliases).filter(
                func.lower(Alias.alias) == inst_name,
                Country.country == inst_country,
            ).first()

        # checking acronyms with institution acronyms
        if not inst and inst_acronym:
            inst: Institution = q2.join(Institution.acronyms).filter(
                func.lower(Acronym.acronym) == inst_acronym,
                Country.country == inst_country,
            ).first()

        # checking bare name with institution name
        if not inst and inst_bare_name:
            inst: Institution = q2.filter(
                func.lower(Institution.name) == inst_bare_name,
                Country.country == inst_country,
            ).first()

        # could not match, or matched before (with another institution)
        if not inst or inst in institutions_list:
            not_mached_list.append(
                {
                    **row,
                    "Problem": "Not Matched" if not inst else "Double Matched",
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

    return (institutions_list, not_mached_list)
