from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rankr.db_models.base import Base


if TYPE_CHECKING:
    from rankr.db_models.institution import Institution


class Country(Base):
    __tablename__ = "country"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(63), unique=True)
    country_code: Mapped[str] = mapped_column(String(2), unique=True)
    region: Mapped[str] = mapped_column(String(15))
    sub_region: Mapped[str | None] = mapped_column(String(63))

    # Relationships
    institutions: Mapped[list["Institution"]] = relationship(back_populates="country")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.country_code}: {self.country}"
