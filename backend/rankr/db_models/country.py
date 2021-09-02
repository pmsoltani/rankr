from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from rankr.db_models.base import Base


class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(63), nullable=False, unique=True)
    country_code = Column(String(2), nullable=False, unique=True)
    region = Column(String(15), nullable=False)
    sub_region = Column(String(63))

    # Relationships
    institutions = relationship("Institution", back_populates="country")

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in self.__table__.c}
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.country_code}: {self.country}"
