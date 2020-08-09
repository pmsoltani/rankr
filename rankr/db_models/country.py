from typing import List

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from config import DBConfig
from rankr.db_models.base import Base
from rankr.db_models.institution import Institution


class Country(Base):
    __tablename__ = "country"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(63), nullable=False, unique=True)
    country_code = Column(String(2), nullable=False, unique=True)
    region = Column(String(15), nullable=False)
    sub_region = Column(String(63))

    # Relationships
    institutions: List[Institution] = relationship(
        "Institution", back_populates="country"
    )

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        kwargs["country"] = DBConfig.country_name_mapper(kwargs["country"])
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.domain}: {self.name}"
