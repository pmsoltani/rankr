from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import enums as e
from rankr.db_models.base import Base


if TYPE_CHECKING:
    from rankr.db_models.institution import Institution


class Link(Base):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id"))
    type: Mapped[e.LinkTypeEnum] = mapped_column(
        Enum(e.LinkTypeEnum),
        index=True,
        server_default=e.LinkTypeEnum.homepage.name,
    )
    link: Mapped[str] = mapped_column(String(1023))

    # Relationships
    institution: Mapped["Institution | None"] = relationship(back_populates="links")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.type}: {self.link}"
