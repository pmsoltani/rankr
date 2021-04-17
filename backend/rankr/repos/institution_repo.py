from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base_repo import BaseRepo


class InstitutionRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Institution
        self.schema = s.InstitutionDB
        super().__init__(db, self.db_model, self.schema)

    def create_institution(
        self, new_institution: s.InstitutionCreate
    ) -> s.InstitutionDB:
        return self._create_object(new_institution)

    def create_db_institution(
        self, new_db_institution: d.Institution
    ) -> d.Institution:
        return self._create_db_object(new_db_institution)

    def create_institutions(
        self, new_institutions: List[s.InstitutionCreate], log: bool = True
    ) -> List[s.InstitutionDB]:
        return self._create_objects(new_institutions, log=log)

    def create_db_institutions(
        self, new_db_institutions: List[d.Institution], log: bool = True
    ) -> List[d.Institution]:
        return self._create_db_objects(new_db_institutions, log=log)

    def get_institution(self, institution_id: int) -> Optional[s.InstitutionDB]:
        return self._get_object_by_id(object_id=institution_id)

    def get_institution_by_grid_id(
        self, grid_id: str
    ) -> Optional[s.InstitutionDB]:
        return self._get_object([self.db_model.grid_id == grid_id])

    def get_institution_by_name(
        self, institution: str
    ) -> Optional[s.InstitutionDB]:
        return self._get_object([self.db_model.institution == institution])

    def get_institutions(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.InstitutionDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
