from sqlalchemy_utils import create_database, database_exists

from config import DBConfig
from rankr.db_models import Base, engine


if not database_exists(engine.url):
    encoding = "utf8mb4" if DBConfig.DIALECT == "mysql" else "utf8"
    create_database(engine.url, encoding=encoding)

Base.metadata.create_all(engine)
