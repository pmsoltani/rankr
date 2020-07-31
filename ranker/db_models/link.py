import enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, Integer, String

from ranker.db_models.base import Base


class LinkTypeEnum(enum.Enum):
    homepage = 1
    qs_profile = 2
    shanghai_profile = 3
    the_profile = 4


class Link(Base):
    __tablename__ = "link"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    type = Column(
        Enum(LinkTypeEnum),
        nullable=False,
        index=True,
        server_default="homepage",
    )
    link = Column(String(1023), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="links")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
