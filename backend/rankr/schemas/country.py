from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationInfo,
    field_validator,
    model_validator,
)

from config import crwc
from rankr.schemas.validators import text_process


class CountryBase(BaseModel):
    # validate_default so country_code/region/sub_region get resolved from the
    # COUNTRIES table even when only `country` is supplied.
    model_config = ConfigDict(validate_default=True)

    id: int | None = None
    country: str
    country_code: str | None = None
    region: str | None = None
    sub_region: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _resolve_country_name_from_country_code(cls, values):
        if not isinstance(values, dict):
            return values
        if values.get("country_code") and not values.get("country"):
            filtered_country = [
                k
                for k, v in crwc.COUNTRIES.items()
                if v["country_code"].lower() == values["country_code"].lower()
            ]
            if not filtered_country:
                raise ValueError("Bad country code")
            values["country"] = filtered_country[0]
        return values

    @field_validator("country", mode="before")
    @classmethod
    def _clean_name(cls, value):
        return text_process(value)

    @field_validator("country")
    @classmethod
    def _resolve_country_name(cls, country: str) -> str:
        try:
            return crwc.COUNTRY_NAMES.get(
                country.strip().replace("-", " ").lower(), country
            )
        except AttributeError:  # country is None
            return country

    @field_validator("country_code", "region", "sub_region")
    @classmethod
    def _resolve_country_info(cls, value, info: ValidationInfo) -> str:
        assert info.field_name is not None
        return crwc.COUNTRIES[info.data["country"]][info.field_name]


class CountryCreate(CountryBase):
    pass
