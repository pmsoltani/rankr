import enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, Integer, String

from config import DBConfig
from rankr.db_models.base import Base


link_types = ["homepage"]
for ranking_system in DBConfig.METRICS["ranking_systems"]:
    link_types.append(f"{ranking_system}_profile")
LinkTypeEnum = enum.Enum("LinkTypeEnum", {type: type for type in link_types},)


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
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)
