from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from config import enums as e
from rankr.db_models.base import Base


class Type(Base):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    type = Column(Enum(e.InstTypeEnum), nullable=False, index=True)

    # Relationships
    institution = relationship("Institution", back_populates="types")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.type}"
