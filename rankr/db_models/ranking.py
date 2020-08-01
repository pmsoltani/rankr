import enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL, Enum, Integer, String

from config import DBConfig
from rankr.db_models.base import Base
from rankr.db_models.institution import Institution


RankingSystemEnum = enum.Enum(
    "RankingSystemEnum",
    {r_s: r_s for r_s in DBConfig.METRICS["ranking_systems"]},
)
MetricEnum = enum.Enum(
    "MetricEnum",
    {m["name"]: m["name"] for m in DBConfig.METRICS["metrics"].values()},
)
ValueTypeEnum = enum.Enum(
    "ValueTypeEnum",
    {m["type"]: m["type"] for m in DBConfig.METRICS["metrics"].values()},
)


class Ranking(Base):
    __tablename__ = "ranking"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    institution_id: int = Column(Integer, ForeignKey("institution.id"))
    ranking_system: RankingSystemEnum = Column(
        Enum(RankingSystemEnum), nullable=False, index=True
    )
    year: int = Column(Integer)
    field: str = Column(String(255), nullable=False)
    subject: str = Column(String(255), nullable=False)
    metric: MetricEnum = Column(Enum(MetricEnum), nullable=False, index=True)
    value: float = Column(DECIMAL(13, 3), nullable=False)
    value_type: ValueTypeEnum = Column(Enum(ValueTypeEnum), nullable=False)

    # Relationships
    institution: Institution = relationship(
        "Institution", back_populates="rankings"
    )

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)
