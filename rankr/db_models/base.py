from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DBConfig

engine = create_engine(DBConfig.DB_URI)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base(bind=engine)
