from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from ranker.db_models.base import Base


class Institution(Base):
    __tablename__ = "institution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    grid_id = Column(String(15), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    wikipedia_url = Column(String(255))
    established = Column(Integer)
    lat = Column(String(63))
    lng = Column(String(63))
    city = Column(String(63))
    state = Column(String(63))
    country = Column(String(63))
    country_code = Column(String(2))

    # Relationships
    acronyms = relationship(
        "Acronym", back_populates="institution", cascade="all, delete-orphan"
    )
    aliases = relationship(
        "Alias", back_populates="institution", cascade="all, delete-orphan"
    )
    links = relationship(
        "Link", back_populates="institution", cascade="all, delete-orphan"
    )
    rankings = relationship(
        "Ranking", back_populates="institution", cascade="all, delete-orphan"
    )
    types = relationship(
        "Type", back_populates="institution", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        kwargs.pop("email_address", None)
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.id} - {self.grid_id}: {self.name}"