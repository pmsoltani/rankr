from sqlalchemy.orm import Session

from rankr import db_models as d
from rankr import schemas as s
from rankr.repos.base import BaseRepo


class CountryRepo(BaseRepo[d.Country]):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Country
        super().__init__(db, self.db_model)

    def create_countries(
        self, new_countries: list[s.CountryCreate], log: bool = True
    ) -> list[d.Country]:
        return self._create_objects(new_countries, log=log)

    def get_countries(
        self,
        search_query: str | None = None,
        offset: int = 0,
        limit: int | None = 25,
    ) -> list[d.Country]:
        return self._get_db_objects(
            search_query=search_query, offset=offset, limit=limit
        )
