from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import dbc

engine = create_engine(dbc.DB_URI)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base(bind=engine)
