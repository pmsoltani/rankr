from typing import Dict
from pydantic import Field, validator
from pydantic.types import SecretStr

from config.base_config import BaseConfig


bc = BaseConfig()


class DBConfig(BaseConfig):
    DB_DRIVER: str = Field(..., env=f"{bc.DIALECT}_DRIVER")
    DB_USER: str = Field(..., env=f"{bc.DIALECT}_USER")
    DB_PASS: SecretStr = Field(..., env=f"{bc.DIALECT}_PASS")
    DB_HOST: str = Field(..., env=f"{bc.DIALECT}_HOST")
    DB_PORT: int = Field(..., env=f"{bc.DIALECT}_PORT")
    DB_NAME: str = Field(..., env=f"{bc.DIALECT}_NAME")
    DB_URL: str = ""

    @validator("DB_URL")
    def _db_url_value(cls, db_url, values) -> str:
        return (
            f"{values['DIALECT']}+{values['DB_DRIVER']}://"
            + f"{values['DB_USER']}:{values['DB_PASS']}@"
            + f"{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        )

    RANKINGS: dict = {}

    @validator("RANKINGS")
    def _load_rankings(cls, rankings, values) -> dict:
        return cls.read_json(values["RANKINGS_FILE"])

    MATCHES: Dict[str, Dict[str, str]] = {}

    @validator("MATCHES")
    def _load_matches(cls, matches, values) -> Dict[str, Dict[str, str]]:
        return cls.read_json(
            values["MATCHES_FILE"],
            lambda d: {(None if not k else k): v for k, v in d.items()},
        )

    def country_name_mapper(self, country: str) -> str:
        try:
            return self.COUNTRY_NAMES.get(
                country.strip().replace("-", " ").lower(), country
            )
        except AttributeError:  # country is None
            return country

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


dbc = DBConfig()
