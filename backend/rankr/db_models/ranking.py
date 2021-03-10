from sqlalchemy import Column, DECIMAL, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from config import enums as e
from rankr.db_models.base import Base


class Ranking(Base):
    __tablename__ = "ranking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    ranking_system = Column(
        Enum(e.RankingSystemEnum), nullable=False, index=True
    )
    ranking_type = Column(Enum(e.RankingTypeEnum), nullable=False, index=True)
    year = Column(Integer)
    field = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    metric = Column(Enum(e.MetricEnum), nullable=False, index=True)
    raw_value = Column(String(63), nullable=False)
    value = Column(DECIMAL(13, 3))
    value_type = Column(Enum(e.ValueTypeEnum), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="rankings")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            f"{self.ranking_system} ({self.year}) | "
            + f"{self.field} ({self.subject}) -> "
            + f"{self.metric}: {self.value}"
        )
