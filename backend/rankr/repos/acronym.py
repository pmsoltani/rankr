from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base import BaseRepo


class AcronymRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Acronym
        self.schema = s.AcronymDB
        super().__init__(db, self.db_model, self.schema)

    def create_acronym(self, new_acronym: s.AcronymCreate) -> s.AcronymDB:
        return self._create_object(new_acronym)

    def create_acronyms(
        self, new_acronyms: List[s.AcronymCreate], log: bool = True
    ) -> List[s.AcronymDB]:
        return self._create_objects(new_acronyms, log=log)

    def get_acronym(self, acronym_id: int) -> Optional[s.AcronymDB]:
        return self._get_object_by_id(object_id=acronym_id)

    def get_acronym_by_name(self, acronym: str) -> Optional[s.AcronymDB]:
        return self._get_object([self.db_model.acronym == acronym])

    def get_acronyms(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.AcronymDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
