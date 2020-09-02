from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from rankr.db_models import Ranking
from rankr.enums import RankingSystemEnum, RankingTypeEnum
from utils import group_by


def get_ranking_systems(db: Session) -> Dict[RankingSystemEnum, List[int]]:
    """Retrieves the available ranking systems and their years.

    Args:
        db (Session): SQLAlchemy session instant to connect to the DB

    Returns:
        Dict[RankingSystemEnum, List[int]]: Available ranking systems
    """
    query = (Ranking.ranking_system, Ranking.year)
    ranking_systems = db.query(*query).group_by(*query).order_by(*query).all()
    result = {}
    for r_s in ranking_systems:
        r_s = r_s._asdict()
        result.setdefault(r_s["ranking_system"], []).append(r_s["year"])
    return result


def get_ranking_table(
    db: Session,
    year: int,
    ranking_system: Optional[RankingSystemEnum] = None,
    ranking_type: RankingTypeEnum = RankingTypeEnum["university ranking"],
    field: str = "All",
    subject: str = "All",
) -> Dict[RankingSystemEnum, List[Ranking]]:
    """[summary]

    Args:
        db (Session): SQLAlchemy session instant to connect to the DB
        year (int): The ranking year of publication
        ranking_system (Optional[RankingSystemEnum], optional): The
        ranking system. Defaults to None.
        ranking_type (RankingTypeEnum, optional): The ranking type.
        Defaults to RankingTypeEnum["university ranking"].
        field (str, optional): The ranking field. Defaults to "All".
        subject (str, optional): The ranking subject. Defaults to "All".

    Returns:
        Dict[RankingSystemEnum, List[Ranking]]: The ranking table
        results, grouped by ranking systems
    """
    filters = (
        Ranking.ranking_type == ranking_type,
        Ranking.year == year,
        Ranking.field == field,
        Ranking.subject == subject,
        Ranking.metric == "Rank",
    )
    if ranking_system:
        filters = (*filters, Ranking.ranking_system == ranking_system)
    rankings = db.query(Ranking).filter(*filters).order_by(Ranking.value).all()
    return group_by(rankings, ["ranking_system"])
