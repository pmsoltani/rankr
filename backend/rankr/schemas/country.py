from typing import Optional

from pydantic import BaseModel, root_validator, validator

from config import crwc
from rankr.schemas.core import OrmBase
from rankr.schemas.validators import text_process


class CountryBase(BaseModel):
    id: Optional[int]
    country: str
    country_code: Optional[str]
    region: Optional[str]
    sub_region: Optional[str]

    # validators
    @root_validator(pre=True)
    def _resolve_country_name_from_country_code(cls, values: dict):
        if values.get("country_code") and not values["country"]:
            filtered_country = [
                k
                for k, v in crwc.COUNTRIES.items()
                if v["country_code"].lower() == values["country_code"].lower()
            ]
            if not filtered_country:
                raise ValueError("Bad country code")
            values["country"] = filtered_country[0]
        return values

    _clean_name = validator("country", allow_reuse=True, pre=True)(text_process)

    @validator("country")
    def _resolve_country_name(cls, country: str) -> str:
        try:
            return crwc.COUNTRY_NAMES.get(
                country.strip().replace("-", " ").lower(), country
            )
        except AttributeError:  # country is None
            return country

    @validator("country_code", "region", "sub_region", always=True)
    def _resolve_country_info(cls, value, values, field) -> str:
        return crwc.COUNTRIES[values["country"]][field.name]


class CountryCreate(CountryBase):
    pass


class CountryOut(CountryBase):
    pass


class CountryDB(OrmBase, CountryOut):
    pass
