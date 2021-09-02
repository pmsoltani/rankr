from typing import List, Optional, Type

import typer
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from rankr import db_models as d


class BaseRepo:
    def __init__(self, db: Session, db_model: Type[d.Base], schema) -> None:
        self.db = db
        self.db_model = db_model
        self.schema = schema

    def _db_to_dict(self, db_object, related_fields: List[str] = []) -> dict:
        if not db_object:
            return {}
        parsed = db_object.__dict__
        for field in related_fields:
            value = getattr(db_object, field)
            parsed[field] = getattr(value, "__dict__", None)
            if isinstance(value, list):
                parsed[field] = [item.__dict__ for item in value]
        return parsed

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
            typer.secho(
                f"Committed {len(new_objects)} new '{object_type}' objects.",
                fg=typer.colors.GREEN,
            )
        return [self.schema.from_orm(db_object) for db_object in db_objects]

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

    def _get_object(self, flt: list = [], related_fields: List[str] = []):
        db_object = self._get_db_object(flt=flt)
        db_object_dict = self._db_to_dict(db_object, related_fields)
        return self.schema(**db_object_dict) if db_object_dict else None

    def _get_db_object_by_relation(self, join, flt: list):
        return self.db.query(self.db_model).join(join).filter(*flt).first()

    def _get_object_by_relation(
        self, join, flt: list, related_fields: List[str] = []
    ):
        db_object = self._get_db_object_by_relation(join=join, flt=flt)
        db_object_dict = self._db_to_dict(db_object, related_fields)
        return self.schema(**db_object_dict) if db_object_dict else None

    def _get_object_by_id(self, object_id: int, related_fields: List[str] = []):
        return self._get_object([self.db_model.id == object_id], related_fields)

    def _get_db_objects(
        self,
        search_query: str = None,
        flt: list = [],
        order_by: list = [],
        offset: int = 0,
        limit: Optional[int] = 25,
    ):
        flt = [self.search(search_query), *flt]
        return (
            self.db.query(self.db_model)
            .filter(*flt)
            .order_by(*order_by)
            .offset(offset)
            .limit(limit or None)
            .all()
        )

    def _get_objects(
        self,
        search_query: str = None,
        flt: list = [],
        order_by: list = [],
        offset: int = 0,
        limit: Optional[int] = 25,
        related_fields: List[str] = [],
    ):
        db_objects = self._get_db_objects(
            search_query=search_query,
            flt=flt,
            offset=offset,
            limit=limit,
            order_by=order_by,
        )
        return [
            self.schema(**self._db_to_dict(db_object, related_fields))
            for db_object in db_objects
        ]

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
