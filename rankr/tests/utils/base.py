from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DBConfig

db_uri = DBConfig.DB_URI + "_test"
engine = create_engine(db_uri, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine)
