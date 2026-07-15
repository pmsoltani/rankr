from typing import Optional, Type

import typer
from sqlalchemy import or_
from sqlalchemy.orm import Session

from rankr import db_models as d


class BaseRepo:
    def __init__(self, db: Session, db_model: Type[d.Base]) -> None:
        self.db = db
        self.db_model = db_model

    def _create_objects(self, new_objects, log: bool = True):
        db_objects = [
            self.db_model(**new_obj.dict(exclude_unset=True)) for new_obj in new_objects
        ]
        self.db.add_all(db_objects)
        self.db.commit()
        if log:
            object_type = self.db_model.__name__
            typer.secho(
                f"Committed {len(new_objects)} new '{object_type}' objects.",
                fg=typer.colors.GREEN,
            )
        return db_objects

    def _create_db_objects(self, new_db_objects, log: bool = True):
        self.db.add_all(new_db_objects)
        self.db.commit()
        if log:
            object_type = self.db_model.__name__
            typer.secho(
                f"Committed {len(new_db_objects)} new '{object_type}' objects.",
                fg=typer.colors.GREEN,
            )
        return new_db_objects

    def _get_db_object(self, flt: list = []):
        return self.db.query(self.db_model).filter(*flt).first()

    def _get_db_object_by_relation(self, join, flt: list):
        return self.db.query(self.db_model).join(join).filter(*flt).first()

    def _get_db_objects(
        self,
        join: Optional[Type[d.Base]] = None,
        distinct: bool = False,
        search_query: str = None,
        flt: list = [],
        order_by: list = [],
        offset: int = 0,
        limit: Optional[int] = 25,
    ):
        flt = [self.search(search_query), *flt]
        query = self.db.query(self.db_model)
        if join:
            query = query.join(join)
        if distinct:
            query = query.distinct()
        return (
            query.filter(*flt)
            .order_by(*order_by)
            .offset(offset)
            .limit(limit or None)
            .all()
        )

    def search(self, search_query: Optional[str]):
        if not search_query:
            return or_()

        search_query = f"%{search_query}%"
        search_chain = ()

        if self.db_model is d.Acronym:
            search_chain = (self.db_model.acronym.ilike(search_query),)

        if self.db_model is d.Alias:
            search_chain = (self.db_model.alias.ilike(search_query),)

        if self.db_model is d.Country:
            search_chain = (
                self.db_model.country.ilike(search_query),
                self.db_model.country_code.ilike(search_query),
                self.db_model.region.ilike(search_query),
                self.db_model.sub_region.ilike(search_query),
            )

        if self.db_model is d.Institution:
            search_chain = (self.db_model.soup.ilike(search_query),)

        if self.db_model is d.Label:
            search_chain = (self.db_model.label.ilike(search_query),)

        return or_(*search_chain)
