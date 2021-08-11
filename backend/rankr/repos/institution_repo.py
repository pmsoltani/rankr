from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from config import dbc
from rankr import db_models as d, schemas as s
from rankr.repos.base_repo import BaseRepo
from utils import fuzzy_matcher


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

    def get_db_institutions(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[d.Institution]:
        return self._get_db_objects(
            search_query=search_query, offset=offset, limit=limit
        )

    def get_institutions(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.InstitutionDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )

    def match_institution(
        self,
        institution_name: str,
        institution_url: str,
        link_type: str,
        country_name: str,
        soup: Dict[str, Dict[str, str]],
    ) -> Tuple[Optional[d.Institution], bool]:
        institution_name = institution_name.strip().lower()
        fuzzy_flag = False
        db_institution: Optional[d.Institution] = None

        # checking grid_id in manual matches
        match = dbc.MATCHES.get(country_name, {}).get(institution_name)
        if match:
            db_institution = self._get_db_object(
                flt=[d.Institution.grid_id == match]
            )

        # checking link with institution links
        if not db_institution:
            flt = [d.Link.link == institution_url, d.Link.type == link_type]
            db_institution = self._get_db_object_by_relation(
                join=d.Institution.links, flt=flt
            )

        # checking name with institution name
        if not db_institution:
            flt = [
                func.lower(d.Institution.name) == institution_name,
                d.Country.country == country_name,
            ]
            db_institution = self._get_db_object_by_relation(
                join=d.Institution.country, flt=flt
            )

        # fuzzy-mataching of strings
        if not db_institution:
            match = fuzzy_matcher(institution_name, country_name, soup)
            if match:
                db_institution = self._get_db_object(
                    flt=[d.Institution.grid_id == match]
                )
                fuzzy_flag = True

        return db_institution, fuzzy_flag
