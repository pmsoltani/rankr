from typing import Optional

from pydantic import BaseModel, validator

from config import crwc
from rankr.schemas.core import OrmBase


class CountryBase(BaseModel):
    id: Optional[int]
    country: str
    country_code: str
    region: str
    sub_region: str

    @validator("country")
    def country_name_mapper(cls, country: str) -> str:
        try:
            return crwc.COUNTRY_NAMES.get(
                country.strip().replace("-", " ").lower(), country
            )
        except AttributeError:  # country is None
            return country


class CountryCreate(CountryBase):
    pass


class CountryOut(CountryBase):
    pass


class CountryDB(CountryBase, OrmBase):
    pass
