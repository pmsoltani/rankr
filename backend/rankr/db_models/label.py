from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rankr.db_models.base import Base


if TYPE_CHECKING:
    from rankr.db_models.institution import Institution


class Label(Base):
    __tablename__ = "label"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id"))
    iso639: Mapped[str] = mapped_column(String(2))
    label: Mapped[str] = mapped_column(String(255))

    # Relationships
    institution: Mapped["Institution | None"] = relationship(back_populates="labels")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.iso639}: {self.label}"
