from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import enums as e
from rankr.db_models.base import Base


if TYPE_CHECKING:
    from rankr.db_models.institution import Institution


class Type(Base):
    __tablename__ = "type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id"))
    type: Mapped[e.InstTypeEnum] = mapped_column(Enum(e.InstTypeEnum), index=True)

    # Relationships
    institution: Mapped["Institution | None"] = relationship(back_populates="types")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.type}"
