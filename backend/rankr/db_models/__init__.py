"""SQLAlchemy models to interact with database tables"""

from rankr.db_models.acronym import Acronym
from rankr.db_models.alias import Alias
from rankr.db_models.base import Base, engine, SessionLocal
from rankr.db_models.country import Country
from rankr.db_models.institution import Institution
from rankr.db_models.label import Label
from rankr.db_models.link import Link
from rankr.db_models.ranking import Ranking
from rankr.db_models.type import Type
