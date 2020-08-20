import enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, Integer, String

from config import DBConfig
from rankr.db_models.base import Base
from rankr.db_models.institution import Institution


link_types = ["homepage"] + DBConfig.RANKINGS["ranking_systems"]
LinkTypeEnum = enum.Enum("LinkTypeEnum", {type: type for type in link_types},)


class Link(Base):
    __tablename__ = "link"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    institution_id: int = Column(Integer, ForeignKey("institution.id"))
    type: LinkTypeEnum = Column(
        Enum(LinkTypeEnum),
        nullable=False,
        index=True,
        server_default="homepage",
    )
    link: str = Column(String(1023), nullable=False)

    # Relationships
    institution: Institution = relationship(
        "Institution", back_populates="links"
    )

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.type}: {self.link}"
