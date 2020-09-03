from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import dbc

db_uri = dbc.DB_URI + "_test"
engine = create_engine(db_uri, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine)
