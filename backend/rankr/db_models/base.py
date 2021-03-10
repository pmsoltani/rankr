from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DatabaseError
from sqlalchemy_utils import create_database

from config import dbc

engine = create_engine(dbc.DB_URL, encoding=dbc.DB_ENCODING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(bind=engine)


def validate_database():
    try:
        create_database(engine.url, encoding=dbc.DB_ENCODING)
    except DatabaseError:
        pass
