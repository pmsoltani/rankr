from typing import List, Optional

from sqlalchemy.orm import Session

from config import crwc, enums as e
from rankr import db_models as d, schemas as s
from rankr.repos.base import BaseRepo


class RankingRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Ranking
        self.schema = s.RankingDB
        super().__init__(db, self.db_model, self.schema)

    def create_ranking(self, new_ranking: s.RankingCreate) -> s.RankingDB:
        return self._create_object(new_ranking)

    def create_rankings(
        self, new_rankings: List[s.RankingCreate], log: bool = True
    ) -> List[s.RankingDB]:
        return self._create_objects(new_rankings, log=log)

    def get_ranking_by_id(self, ranking_id: int) -> Optional[s.RankingDB]:
        return self._get_object_by_id(object_id=ranking_id)

    def get_rankings_by_institution_ids(
        self,
        institution_ids: List[int],
        ranking_system: e.RankingSystemEnum,
        ranking_type: e.RankingTypeEnum,
        metric: e.MetricEnum,
        field: str = "All",
        subject: str = "All",
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.RankingDB]:
        flt = [
            self.db_model.institution_id.in_(institution_ids),
            self.db_model.ranking_system == ranking_system,
            self.db_model.ranking_type == ranking_type,
            self.db_model.field == field,
            self.db_model.subject == subject,
            self.db_model.metric == metric,
        ]
        order_by = [
            self.db_model.institution_id,
            self.db_model.metric,
            self.db_model.year,
        ]
        return self._get_objects(
            flt=flt, offset=offset, limit=limit, order_by=order_by
        )

    def get_rankings(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.RankingDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )

    def get_ranks_by_institution_id(
        self, institution_id: int
    ) -> List[s.RankingDB]:
        flt = [
            self.db_model.institution_id == institution_id,
            self.db_model.ranking_type
            == e.RankingTypeEnum["university ranking"],
            self.db_model.metric == e.MetricEnum["Rank"],
        ]
        order_by = [self.db_model.ranking_system, self.db_model.year]
        return self._get_objects(flt=flt, order_by=order_by, limit=None)

    def get_stats_by_institution_id(
        self, institution_id: int
    ) -> List[s.RankingDB]:
        year = self.get_latest_year(
            institution_id=institution_id,
            ranking_system=e.RankingSystemEnum["the"],
            ranking_type=e.RankingTypeEnum["university ranking"],
        )
        if not year:
            return []
        flt = [
            self.db_model.institution_id == institution_id,
            self.db_model.ranking_system == e.RankingSystemEnum["the"],
            self.db_model.ranking_type
            == e.RankingTypeEnum["university ranking"],
            self.db_model.metric.in_(crwc.RANKINGS["stat_metrics"]),
            self.db_model.year == year,
        ]
        order_by = [self.db_model.year]
        return self._get_objects(flt=flt, order_by=order_by, limit=0)

    def get_scores_by_institution_id(
        self, institution_id: int
    ) -> List[s.RankingDB]:
        score_metrics = [m for m in e.MetricEnum if "Score" in m.name]
        flt = [
            self.db_model.institution_id == institution_id,
            self.db_model.ranking_type
            == e.RankingTypeEnum["university ranking"],
            self.db_model.metric.in_(score_metrics),
        ]
        order_by = [self.db_model.ranking_system, self.db_model.year]
        return self._get_objects(flt=flt, order_by=order_by, limit=0)

    def get_ranking_systems(self):
        order_by = [self.db_model.ranking_system, self.db_model.year]
        ranking_tables = (
            self.db.query(self.db_model.ranking_system, self.db_model.year)
            .order_by(*order_by)
            .distinct()
            .all()
        )
        result = {}
        for item in ranking_tables:
            try:
                result[item["ranking_system"]].append(item["year"])
            except KeyError:
                result[item["ranking_system"]] = [item["year"]]
        return result

    def get_ranking_table(
        self,
        ranking_system: e.RankingSystemEnum,
        ranking_type: e.RankingTypeEnum,
        year: int,
        field: str = "All",
        subject: str = "All",
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.RankingTableRow]:
        flt = [
            self.db_model.year == year,
            self.db_model.ranking_system == ranking_system,
            self.db_model.ranking_type == ranking_type,
            self.db_model.metric == e.MetricEnum["Rank"],
            self.db_model.field == field,
            self.db_model.subject == subject,
        ]
        order_by = [self.db_model.value]
        db_rankings: List[d.Ranking] = self._get_db_objects(
            flt=flt, order_by=order_by, offset=offset, limit=limit
        )

        rankings = []
        for db_ranking in db_rankings:
            institution = s.InstitutionDB(
                **{
                    **db_ranking.institution.__dict__,
                    "country": db_ranking.institution.country,
                }
            )
            ranking = s.RankingTableRow(
                **{**db_ranking.__dict__, "institution": institution}
            )
            rankings.append(ranking)

        return rankings

    def get_latest_year(
        self,
        institution_id: int,
        ranking_system: e.RankingSystemEnum,
        ranking_type: e.RankingTypeEnum,
        field: str = "All",
        subject: str = "All",
    ) -> Optional[int]:
        flt = [
            self.db_model.institution_id == institution_id,
            self.db_model.ranking_system == ranking_system,
            self.db_model.ranking_type == ranking_type,
            self.db_model.field == field,
            self.db_model.subject == subject,
        ]
        order_by = [self.db_model.year.desc()]
        latest_ranking = self._get_objects(flt=flt, order_by=order_by, limit=1)
        return latest_ranking[0].year if latest_ranking else None
