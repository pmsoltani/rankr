from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import enums as e
from rankr.db_models.base import Base


if TYPE_CHECKING:
    from rankr.db_models.institution import Institution


class Ranking(Base):
    __tablename__ = "ranking"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id"))
    ranking_system: Mapped[e.RankingSystemEnum] = mapped_column(
        Enum(e.RankingSystemEnum), index=True
    )
    ranking_type: Mapped[e.RankingTypeEnum] = mapped_column(
        Enum(e.RankingTypeEnum), index=True
    )
    year: Mapped[int | None] = mapped_column()
    field: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    metric: Mapped[e.MetricEnum] = mapped_column(Enum(e.MetricEnum), index=True)
    raw_value: Mapped[str | None] = mapped_column(String(63))
    value: Mapped[Decimal | None] = mapped_column(DECIMAL(13, 3))
    value_type: Mapped[e.ValueTypeEnum] = mapped_column(Enum(e.ValueTypeEnum))

    # Relationships
    institution: Mapped["Institution | None"] = relationship(back_populates="rankings")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            f"{self.ranking_system} ({self.year}) | "
            + f"{self.field} ({self.subject}) -> "
            + f"{self.metric}: {self.value}"
        )
