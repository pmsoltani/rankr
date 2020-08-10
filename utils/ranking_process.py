import re
from typing import Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from config import DBConfig
from rankr.db_models import Acronym, Alias, Country, Institution, Link
from utils import get_row, metrics_process, nullify


def ranking_process(
    db: Session, file_path: str
) -> Tuple[List[Institution], List[Dict[str, str]]]:
    institutions_list = []
    not_mached_list = []

    rows = get_row(file_path)
    for row in rows:
        nullify(row)
        link_type = row["Ranking System"]
        inst_name = row["Institution"].lower()
        inst_country = row["Country"]
        if inst_country == "Hong Kong":
            # The GRID database lists institutions in 'Hong Kong' as Chinese
            inst_country == "China"
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

        inst = None

        # checking link with institution links
        link: Link = db.query(Link).filter(
            Link.link == inst_url, Link.type == link_type
        ).first()
        if link:
            inst = link.institution

        # checking grid_id in manual matches
        if not inst:
            if DBConfig.MATCHES.get(inst_name):
                inst: Institution = db.query(Institution).filter(
                    Institution.grid_id == DBConfig.MATCHES[inst_name]
                ).first()

        # checking name with institution name
        if not inst:
            inst: Institution = db.query(Institution).join(
                Institution.country
            ).filter(
                func.lower(Institution.name) == inst_name,
                Country.country == inst_country,
            ).first()

        # checking name with institution acronyms
        if not inst:
            inst: Institution = db.query(Institution).join(
                Institution.country
            ).join(Institution.acronyms).filter(
                func.lower(Acronym.acronym) == inst_name,
                Country.country == inst_country,
            ).first()

        # checking name with institution aliases
        if not inst:
            inst: Institution = db.query(Institution).join(
                Institution.country
            ).join(Institution.aliases).filter(
                func.lower(Alias.alias) == inst_name,
                Country.country == inst_country,
            ).first()

        # checking acronyms with institution acronyms
        if not inst and inst_acronym:
            inst: Institution = db.query(Institution).join(
                Institution.country
            ).join(Institution.acronyms).filter(
                func.lower(Acronym.acronym) == inst_acronym,
                Country.country == inst_country,
            ).first()

        # checking bare name with institution name
        if not inst and inst_bare_name:
            inst: Institution = db.query(Institution).join(
                Institution.country
            ).filter(
                func.lower(Institution.name) == inst_bare_name,
                Country.country == inst_country,
            ).first()

        # could not match, or matched before (with another institution)
        if not inst or inst in institutions_list:
            not_mached_list.append(
                {
                    "Institution": inst_name,
                    "Country": inst_country,
                    "Problem": "Not Matched" if not inst else "Double Matched",
                    "URL": inst_url,
                    "Ranking System": row["Ranking System"],
                    "Ranking Type": row["Ranking Type"],
                    "Year": row["Year"],
                    "Field": row["Field"],
                    "Subject": row["Subject"],
                }
            )
            continue

        ranking_metrics = metrics_process(row)
        inst_link_types = [link.type.name for link in inst.links]
        if link_type not in inst_link_types and inst_url:
            inst.links.append(Link(type=link_type, link=inst_url))
        inst.rankings.extend(ranking_metrics)
        institutions_list.append(inst)

    return (institutions_list, not_mached_list)
