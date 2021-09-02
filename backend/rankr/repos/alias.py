from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base import BaseRepo


class AliasRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Alias
        self.schema = s.AliasDB
        super().__init__(db, self.db_model, self.schema)

    def create_alias(self, new_alias: s.AliasCreate) -> s.AliasDB:
        return self._create_object(new_alias)

    def create_aliases(
        self, new_aliases: List[s.AliasCreate], log: bool = True
    ) -> List[s.AliasDB]:
        return self._create_objects(new_aliases, log=log)

    def get_alias(self, alias_id: int) -> Optional[s.AliasDB]:
        return self._get_object_by_id(object_id=alias_id)

    def get_alias_by_name(self, alias: str) -> Optional[s.AliasDB]:
        return self._get_object([self.db_model.alias == alias])

    def get_aliases(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.AliasDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
