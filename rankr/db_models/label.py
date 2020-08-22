from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from rankr.db_models.base import Base
from rankr.db_models.institution import Institution


class Label(Base):
    __tablename__ = "label"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    institution_id: int = Column(Integer, ForeignKey("institution.id"))
    iso639: str = Column(String(2), nullable=False)
    label: str = Column(String(255), nullable=False)

    # Relationships
    institution: Institution = relationship(
        "Institution", back_populates="labels"
    )

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.iso639}: {self.label}"
