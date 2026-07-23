from sqlalchemy import func
from sqlalchemy.orm import Session

from config import dbc
from rankr import db_models as d
from rankr.repos.base import BaseRepo
from utils import fuzzy_matcher, match_ror_affiliation


class InstitutionRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Institution
        super().__init__(db, self.db_model)

    def create_db_institutions(
        self, new_db_institutions: list[d.Institution], log: bool = True
    ) -> list[d.Institution]:
        return self._create_db_objects(new_db_institutions, log=log)

    def get_institution_by_ror_id(self, ror_id: str) -> d.Institution | None:
        return self._get_db_object([d.Institution.ror_id == ror_id])

    def get_db_institutions(
        self,
        search_query: str | None = None,
        offset: int = 0,
        limit: int | None = 25,
    ) -> list[d.Institution]:
        return self._get_db_objects(
            search_query=search_query, offset=offset, limit=limit
        )

    def match_institution(
        self,
        institution_name: str,
        institution_url: str,
        link_type: str,
        country_name: str,
        soup: dict[str, dict[str, str]],
        education_rors: set[str] | None = None,
        cache: dict[str, dict[str, str]] | None = None,
        use_api: bool = True,
    ) -> tuple[d.Institution | None, bool]:
        raw_name = institution_name.strip()
        institution_name = raw_name.lower()
        fuzzy_flag = False
        db_institution: d.Institution | None = None

        # checking ror_id in manual matches (curated overrides win over all)
        match = dbc.MATCHES.get(country_name, {}).get(institution_name)
        if match:
            db_institution = self._get_db_object(flt=[d.Institution.ror_id == match])

        # affiliation cache: a ranking URL is stable per institution, while the
        # displayed name could drift year to year, so try the link first, then the name.
        if not db_institution and cache is not None:
            ror = (
                cache.get("links", {}).get(institution_url) if institution_url else None
            )
            if not ror:
                ror = cache.get("names", {}).get(institution_name)
            if ror:
                db_institution = self._get_db_object(flt=[d.Institution.ror_id == ror])

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

        # ROR affiliation matcher (chosen:true); tuned for messy strings
        if not db_institution and use_api:
            query = f"{raw_name}, {country_name}" if country_name else raw_name
            match = match_ror_affiliation(query)
            if match:
                db_institution = self._get_db_object(
                    flt=[d.Institution.ror_id == match]
                )

        # local fuzzy fallback (offline / no chosen match); lower confidence
        if not db_institution:
            match = fuzzy_matcher(institution_name, country_name, soup, education_rors)
            if match:
                db_institution = self._get_db_object(
                    flt=[d.Institution.ror_id == match]
                )
                fuzzy_flag = True

        # remember confident matches so next year's entry with the same URL resolves
        # instantly; fuzzy matches stay uncached so they are re-tried and re-flagged
        # each crawl.
        if db_institution and cache is not None and not fuzzy_flag:
            cache.setdefault("names", {})[institution_name] = db_institution.ror_id
            if institution_url:
                cache.setdefault("links", {})[institution_url] = db_institution.ror_id

        return db_institution, fuzzy_flag
