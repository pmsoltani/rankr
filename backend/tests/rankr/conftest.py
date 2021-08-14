from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import create_database

from config import dbc
from main import app
from rankr.api import deps
from rankr.db_models import Base, Country, Institution, Ranking
from tests.rankr.utils import (
    engine,
    fake_institutions,
    fake_rankings,
    fill_countries,
    override_get_db,
    TestingSessionLocal,
)


app.dependency_overrides[deps.get_db] = override_get_db


@pytest.fixture(scope="session")
def db() -> Generator:
    try:
        encoding = "utf8mb4" if dbc.DIALECT == "mysql" else "utf8"
        create_database(engine.url, encoding=encoding)
    except Exception:
        pass

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal()


@pytest.fixture(scope="session")
def data(db: Session):
    db.query(Ranking).delete()
    db.query(Institution).delete()
    db.query(Country).delete()

    countries = fill_countries(dbc.COUNTRIES_FILE)
    institutions = fake_institutions(10)
    db.add_all(countries)
    db.commit()

    for institution in institutions:
        institution.rankings = fake_rankings()
        db.add(institution)
    db.commit()
    return db


@pytest.fixture(scope="module")
def client(data) -> Generator:
    with TestClient(app) as c:
        yield c
