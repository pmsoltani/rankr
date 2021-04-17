from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base_repo import BaseRepo


class CountryRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Country
        self.schema = s.CountryDB
        super().__init__(db, self.db_model, self.schema)

    def create_country(self, new_country: s.CountryCreate) -> s.CountryDB:
        return self._create_object(new_country)

    def create_countries(
        self, new_countries: List[s.CountryCreate], log: bool = True
    ) -> List[s.CountryDB]:
        return self._create_objects(new_countries, log=log)

    def get_country(self, country_id: int) -> Optional[s.CountryDB]:
        return self._get_object_by_id(object_id=country_id)

    def get_country_by_name(self, country: str) -> Optional[s.CountryDB]:
        return self._get_object([self.db_model.country == country])

    def get_countries(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.CountryDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
