from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import dbc

db_url = dbc.DB_URL + "_test"
engine = create_engine(db_url, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine)
