"""SQLAlchemy models to interact with database tables"""

from rankr.db_models.acronym import Acronym  # noqa
from rankr.db_models.alias import Alias  # noqa
from rankr.db_models.base import Base, engine, SessionLocal  # noqa
from rankr.db_models.country import Country  # noqa
from rankr.db_models.institution import Institution  # noqa
from rankr.db_models.label import Label  # noqa
from rankr.db_models.link import Link  # noqa
from rankr.db_models.ranking import Ranking  # noqa
from rankr.db_models.type import Type  # noqa
