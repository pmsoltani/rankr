from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from rankr.db_models.base import Base


class Institution(Base):
    __tablename__ = "institution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    grid_id = Column(String(15), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    established = Column(Integer)
    lat = Column(String(63))
    lng = Column(String(63))
    city = Column(String(63))
    state = Column(String(63))
    country_id = Column(Integer, ForeignKey("country.id"))
    soup = Column(String(1000))

    # Relationships
    acronyms = relationship(
        "Acronym", back_populates="institution", cascade="all, delete-orphan"
    )
    aliases = relationship(
        "Alias", back_populates="institution", cascade="all, delete-orphan"
    )
    country = relationship("Country", back_populates="institutions")
    labels = relationship(
        "Label", back_populates="institution", cascade="all, delete-orphan"
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
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        if self.id:
            return f"{self.id} - {self.grid_id}: {self.name}"
        return f"{self.grid_id}: {self.name}"
