from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from config import enums as e
from rankr import db_models as d
from utils import group_by


def get_ranking_systems(db: Session) -> Dict[e.RankingSystemEnum, List[int]]:
    """Retrieves the available ranking systems and their years.

    Args:
        db (Session): SQLAlchemy session instant to connect to the DB

    Returns:
        Dict[e.RankingSystemEnum, List[int]]: Available ranking systems
    """
    query = (d.Ranking.ranking_system, d.Ranking.year)
    ranking_systems = db.query(*query).group_by(*query).order_by(*query).all()
    result = {}
    for r_s in ranking_systems:
        r_s = r_s._asdict()
        result.setdefault(r_s["ranking_system"], []).append(r_s["year"])
    return result


def get_ranking_table(
    db: Session,
    year: int,
    ranking_system: Optional[e.RankingSystemEnum] = None,
    ranking_type: e.RankingTypeEnum = e.RankingTypeEnum["university ranking"],
    field: str = "All",
    subject: str = "All",
) -> Dict[e.RankingSystemEnum, List[d.Ranking]]:
    """[summary]

    Args:
        db (Session): SQLAlchemy session instant to connect to the DB
        year (int): The ranking year of publication
        ranking_system (Optional[e.RankingSystemEnum], optional): The
        ranking system. Defaults to None.
        ranking_type (e.RankingTypeEnum, optional): The ranking type.
        Defaults to e.RankingTypeEnum["university ranking"].
        field (str, optional): The ranking field. Defaults to "All".
        subject (str, optional): The ranking subject. Defaults to "All".

    Returns:
        Dict[e.RankingSystemEnum, List[Ranking]]: The ranking table
        results, grouped by ranking systems
    """
    filters = (
        d.Ranking.ranking_type == ranking_type,
        d.Ranking.year == year,
        d.Ranking.field == field,
        d.Ranking.subject == subject,
        d.Ranking.metric == "Rank",
    )
    if ranking_system:
        filters = (*filters, d.Ranking.ranking_system == ranking_system)
    rankings = (
        db.query(d.Ranking).filter(*filters).order_by(d.Ranking.value).all()
    )
    return group_by(rankings, ["ranking_system"])
