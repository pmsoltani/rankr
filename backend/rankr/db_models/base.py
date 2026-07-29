import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import dbc


engine = create_engine(dbc.DB_URL)
# 2.0 sessions are non-autocommit; autoflush stays off for the bulk imports.
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    # SQLite disables foreign-key enforcement by default; turn it on so the
    # relationships/cascades behave. WAL improves throughput for the bulk
    # GRID/ranking imports.
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
