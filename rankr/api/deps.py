from typing import Generator

from sqlalchemy.orm import Session

from rankr.db_models import SessionLocal


def get_db() -> Generator[Session, None, None]:
    try:
        db: Session = SessionLocal()
        yield db
    finally:
        db.close()
