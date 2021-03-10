from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from rankr.db_models.base import Base


class Label(Base):
    __tablename__ = "label"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    iso639 = Column(String(2), nullable=False)
    label = Column(String(255), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="labels")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.iso639}: {self.label}"
