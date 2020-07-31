from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from ranker.db_models.base import Base


class Alias(Base):
    __tablename__ = "alias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    alias = Column(String(255), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="aliases")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
