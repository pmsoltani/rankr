from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base_repo import BaseRepo


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

    def get_ranking(self, ranking_id: int) -> Optional[s.RankingDB]:
        return self._get_object_by_id(object_id=ranking_id)

    def get_ranking_by_name(self, ranking: str) -> Optional[s.RankingDB]:
        return self._get_object([self.db_model.ranking == ranking])

    def get_rankings(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.RankingDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
