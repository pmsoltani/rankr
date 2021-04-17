from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base_repo import BaseRepo


class LinkRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Link
        self.schema = s.LinkDB
        super().__init__(db, self.db_model, self.schema)

    def create_link(self, new_link: s.LinkCreate) -> s.LinkDB:
        return self._create_object(new_link)

    def create_links(
        self, new_links: List[s.LinkCreate], log: bool = True
    ) -> List[s.LinkDB]:
        return self._create_objects(new_links, log=log)

    def get_link(self, link_id: int) -> Optional[s.LinkDB]:
        return self._get_object_by_id(object_id=link_id)

    def get_link_by_name(self, link: str) -> Optional[s.LinkDB]:
        return self._get_object([self.db_model.link == link])

    def get_links(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.LinkDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
