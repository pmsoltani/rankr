from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from config import enums as e
from rankr.db_models.base import Base


class Link(Base):
    __tablename__ = "link"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    type = Column(
        Enum(e.LinkTypeEnum),
        nullable=False,
        index=True,
        server_default=e.LinkTypeEnum.homepage.name,
    )
    link = Column(String(1023), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="links")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.type}: {self.link}"
