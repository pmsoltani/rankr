from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from rankr.db_models import Ranking
from rankr.enums import RankingSystemEnum, RankingTypeEnum
from utils import group_by


def get_ranking_systems(db: Session):
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
