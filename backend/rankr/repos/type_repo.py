from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base_repo import BaseRepo


class TypeRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Type
        self.schema = s.TypeDB
        super().__init__(db, self.db_model, self.schema)

    def create_type(self, new_type: s.TypeCreate) -> s.TypeDB:
        return self._create_object(new_type)

    def create_types(
        self, new_types: List[s.TypeCreate], log: bool = True
    ) -> List[s.TypeDB]:
        return self._create_objects(new_types, log=log)

    def get_type(self, type_id: int) -> Optional[s.TypeDB]:
        return self._get_object_by_id(object_id=type_id)

    def get_type_by_name(self, type: str) -> Optional[s.TypeDB]:
        return self._get_object([self.db_model.type == type])

    def get_types(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.TypeDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
