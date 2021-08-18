from contextlib import closing
from typing import Callable, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from rankr import db_models as d
from rankr.repos.base import BaseRepo


def get_db() -> Generator[Session, None, None]:
    """Yields a SQLAlchemy session for the CRUD operations."""
    db: Session
    with closing(d.SessionLocal()) as db:
        yield db


def get_repo(RepoClass) -> Callable:
    def get_repo(db: Session = Depends(get_db)) -> BaseRepo:
        return RepoClass(db)

    return get_repo
