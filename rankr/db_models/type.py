import enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, Integer

from rankr.db_models.base import Base
from rankr.db_models.institution import Institution


class InstTypeEnum(enum.Enum):
    Archive = 1
    Company = 2
    Education = 3
    Facility = 4
    Government = 5
    Healthcare = 6
    Nonprofit = 7
    Other = 8


class Type(Base):
    __tablename__ = "type"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    institution_id: int = Column(Integer, ForeignKey("institution.id"))
    type: InstTypeEnum = Column(Enum(InstTypeEnum), nullable=False, index=True)

    # Relationships
    institution: Institution = relationship(
        "Institution", back_populates="types"
    )

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)
