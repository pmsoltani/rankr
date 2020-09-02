from typing import Generator

from sqlalchemy.orm import Session

from rankr.tests.utils.base import TestingSessionLocal


def override_get_db() -> Generator[Session, None, None]:
    try:
        db: Session = TestingSessionLocal()
        yield db
    finally:
        db.close()
