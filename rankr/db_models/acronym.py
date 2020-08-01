from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from rankr.db_models.base import Base


class Acronym(Base):
    __tablename__ = "acronym"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    acronym = Column(String(255), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="acronyms")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return self.acronym
