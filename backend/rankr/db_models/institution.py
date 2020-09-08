from typing import List, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from rankr.db_models.base import Base

if TYPE_CHECKING:
    from rankr.db_models.acronym import Acronym
    from rankr.db_models.alias import Alias
    from rankr.db_models.country import Country
    from rankr.db_models.label import Label
    from rankr.db_models.link import Link
    from rankr.db_models.ranking import Ranking
    from rankr.db_models.type import Type


class Institution(Base):
    __tablename__ = "institution"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    grid_id: str = Column(String(15), unique=True, nullable=False)
    name: str = Column(String(255), nullable=False)
    wikipedia_url: str = Column(String(255))
    established: int = Column(Integer)
    lat: str = Column(String(63))
    lng: str = Column(String(63))
    city: str = Column(String(63))
    state: str = Column(String(63))
    country_id: int = Column(Integer, ForeignKey("country.id"))
    soup: str = Column(String(1000))

    # Relationships
    acronyms: List["Acronym"] = relationship(
        "Acronym", back_populates="institution", cascade="all, delete-orphan"
    )
    aliases: List["Alias"] = relationship(
        "Alias", back_populates="institution", cascade="all, delete-orphan"
    )
    country: "Country" = relationship("Country", back_populates="institutions")
    labels: List["Label"] = relationship(
        "Label", back_populates="institution", cascade="all, delete-orphan"
    )
    links: List["Link"] = relationship(
        "Link", back_populates="institution", cascade="all, delete-orphan"
    )
    rankings: List["Ranking"] = relationship(
        "Ranking", back_populates="institution", cascade="all, delete-orphan"
    )
    types: List["Type"] = relationship(
        "Type", back_populates="institution", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        if self.id:
            return f"{self.id} - {self.grid_id}: {self.name}"
        return f"{self.grid_id}: {self.name}"
