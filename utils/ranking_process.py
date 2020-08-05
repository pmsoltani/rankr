import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from config import DBConfig
from rankr.db_models import Acronym, Alias, Institution, Link
from utils import get_row, metrics_process, nullify


def ranking_process(db: Session, file_path: str):
    rows = get_row(file_path)

    institutions_list = []
    for row in rows:
        nullify(row)
        ranking_system = row["Ranking System"]
        link_type = f"{ranking_system}_profile"
        inst_name = row["Institution"].lower()
        inst_country = row["Country"]
        inst_url = row["URL"]
        inst_acronym = re.search(r"\((.*?)\)$", row["Institution"])
        if inst_acronym:
            # institution acronym:
            # "universiti malaya (um)" -> "um"
            inst_acronym = inst_acronym.group(1).lower()
            # institution name without acronym:
            # "universiti malaya (um)" -> "universiti malaya"
            inst_bare_name = re.search(r"^(.*?)\(", row["Institution"])
            inst_bare_name = inst_bare_name.group(1).strip().lower()

        link: Link = db.query(Link).filter(
            Link.link == inst_url, Link.type == link_type
        ).first()
        if link and link.institution.country.country == inst_country:
            inst = link.institution
        elif inst_name in DBConfig.MATCHES:
            inst: Institution = db.query(Institution).filter(
                Institution.grid_id == DBConfig.MATCHES[inst_name]
            ).first()
        else:
            inst: Institution = db.query(Institution).filter(
                func.lower(Institution.name) == inst_name
            ).first()
            if not inst or not inst.country.country == inst_country:
                alias: Alias = db.query(Alias).filter(
                    func.lower(Alias.alias) == inst_name
                ).first()
                if alias and alias.institution.country.country == inst_country:
                    inst = alias.institution
                else:
                    if inst_acronym:
                        acro: Acronym = db.query(Acronym).filter(
                            func.lower(Acronym.acronym) == inst_acronym
                        ).first()
                        if (
                            acro
                            and acro.institution.country.country == inst_country
                        ):
                            inst = acro.institution
                        else:
                            inst: Institution = db.query(Institution).filter(
                                func.lower(Institution.name) == inst_bare_name,
                            ).first()
                            if (
                                not inst
                                or not inst.country.country == inst_country
                            ):
                                print("NOT FOUND:", inst_name)

        if inst:
            ranking_metrics = metrics_process(row)

            if link_type not in [link.type.name for link in inst.links]:
                inst.links.append(Link(type=link_type, link=inst_url))
            inst.rankings.extend(ranking_metrics)
            institutions_list.append(inst)

    return institutions_list
