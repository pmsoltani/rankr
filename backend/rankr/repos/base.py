from collections.abc import Sequence
from typing import Any

import typer
from sqlalchemy import or_, select, true
from sqlalchemy.orm import Session

from rankr import db_models as d


class BaseRepo[ModelT: d.Base]:
    def __init__(self, db: Session, db_model: type[ModelT]) -> None:
        self.db = db
        self.db_model = db_model

    def _log_committed(self, count: int) -> None:
        typer.secho(
            f"Committed {count} new '{self.db_model.__name__}' objects.",
            fg=typer.colors.GREEN,
        )

    def _create_objects(self, new_objects, log: bool = True) -> list[ModelT]:
        db_objects = [
            self.db_model(**obj.model_dump(exclude_unset=True)) for obj in new_objects
        ]
        self.db.add_all(db_objects)
        self.db.commit()
        if log:
            self._log_committed(len(db_objects))
        return db_objects

    def _create_db_objects(
        self, new_db_objects: list[ModelT], log: bool = True
    ) -> list[ModelT]:
        self.db.add_all(new_db_objects)
        self.db.commit()
        if log:
            self._log_committed(len(new_db_objects))
        return new_db_objects

    def _get_db_object(self, flt: Sequence[Any] = ()) -> ModelT | None:
        return self.db.scalars(select(self.db_model).where(*flt)).first()

    def _get_db_object_by_relation(
        self, join: Any, flt: Sequence[Any]
    ) -> ModelT | None:
        return self.db.scalars(select(self.db_model).join(join).where(*flt)).first()

    def _get_db_objects(
        self,
        join: Any = None,
        distinct: bool = False,
        search_query: str | None = None,
        flt: Sequence[Any] = (),
        order_by: Sequence[Any] = (),
        offset: int = 0,
        limit: int | None = 25,
    ) -> list[ModelT]:
        stmt = select(self.db_model).where(self.search(search_query), *flt)
        if join is not None:
            stmt = stmt.join(join)
        if distinct:
            stmt = stmt.distinct()
        stmt = stmt.order_by(*order_by).offset(offset).limit(limit or None)
        return list(self.db.scalars(stmt).all())

    def search(self, search_query: str | None):
        if not search_query:
            return true()  # no filter (SQLAlchemy 2.0: empty or_() is invalid)

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
