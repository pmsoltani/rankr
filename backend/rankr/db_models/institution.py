from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rankr.db_models.base import Base


if TYPE_CHECKING:
    from rankr.db_models.acronym import Acronym
    from rankr.db_models.alias import Alias
    from rankr.db_models.country import Country
    from rankr.db_models.label import Label
    from rankr.db_models.link import Link
    from rankr.db_models.ranking import Ranking
    from rankr.db_models.type import Type


class Institution(Base):
    __tablename__ = "institution"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ror_id: Mapped[str] = mapped_column(String(9), unique=True)
    # Retired identifier kept for provenance & legacy /i/grid.x redirects.
    grid_id: Mapped[str | None] = mapped_column(String(15), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    established: Mapped[int | None] = mapped_column()
    lat: Mapped[str | None] = mapped_column(String(63))
    lng: Mapped[str | None] = mapped_column(String(63))
    city: Mapped[str | None] = mapped_column(String(63))
    state: Mapped[str | None] = mapped_column(String(63))
    country_id: Mapped[int | None] = mapped_column(ForeignKey("country.id"))
    soup: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    acronyms: Mapped[list["Acronym"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    aliases: Mapped[list["Alias"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    country: Mapped["Country | None"] = relationship(back_populates="institutions")
    labels: Mapped[list["Label"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    links: Mapped[list["Link"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    rankings: Mapped[list["Ranking"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )
    types: Mapped[list["Type"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        if self.id:
            return f"{self.id} - {self.ror_id}: {self.name}"
        return f"{self.ror_id}: {self.name}"
