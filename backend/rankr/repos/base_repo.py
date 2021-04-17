from typing import Iterable, Optional, Type

from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typer import secho
from typer.colors import GREEN

from rankr import db_models as d


class BaseRepo:
    def __init__(self, db: Session, db_model: Type[d.Base], schema) -> None:
        self.db = db
        self.db_model = db_model
        self.schema = schema

    def _create_object(self, new_object: BaseModel):
        db_object = self.db_model(**new_object.dict(exclude_unset=True))
        self.db.add(db_object)
        self.db.commit()
        return self.schema.from_orm(db_object)

    def _create_db_object(self, new_db_object: d.Base):
        self.db.add(new_db_object)
        self.db.commit()
        return new_db_object

    def _create_objects(self, new_objects, log: bool = True):
        db_objects = [
            self.db_model(**new_obj.dict(exclude_unset=True))
            for new_obj in new_objects
        ]
        self.db.add_all(db_objects)
        self.db.commit()
        if log:
            object_type = self.db_model.__name__
            secho(
                f"Committed {len(new_objects)} new '{object_type}' objects.",
                fg=GREEN,
            )
        return [self.schema.from_orm(db_object) for db_object in db_objects]

    def _create_db_objects(self, new_db_objects, log: bool = True):
        self.db.add_all(new_db_objects)
        self.db.commit()
        if log:
            object_type = self.db_model.__name__
            secho(
                f"Committed {len(new_db_objects)} new '{object_type}' objects.",
                fg=GREEN,
            )
        return new_db_objects

    def _get_object(self, flt: Iterable = []):
        db_object = self.db.query(self.db_model).filter(*flt).first()
        return self.schema.from_orm(db_object) if db_object else None

    def _get_object_by_id(self, object_id: int):
        return self._get_object([self.db_model.id == object_id])

    def _get_objects(
        self,
        search_query: str = None,
        flt: Iterable = [],
        offset: int = 0,
        limit: Optional[int] = 25,
    ):
        flt = [self.search(search_query), *flt]
        db_objects = (
            self.db.query(self.db_model)
            .filter(*flt)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self.schema.from_orm(db_object) for db_object in db_objects]

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
            search_chain = (
                self.db_model.name.ilike(search_query),
                self.db_model.city.ilike(search_query),
                self.db_model.state.ilike(search_query),
            )

        if self.db_model is d.Label:
            search_chain = (self.db_model.label.ilike(search_query),)

        return or_(*search_chain)
