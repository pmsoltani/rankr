from typing import Generator

from sqlalchemy.orm import Session

from rankr import db_models as d


def get_db() -> Generator[Session, None, None]:
    """Yields a SQLAlchemy session for the CRUD operations."""
    db: Session = d.SessionLocal()
    try:
        yield db
    finally:
        db.close()
