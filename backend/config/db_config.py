from typing import Dict
from pydantic import Field, validator

from config.base_config import BaseConfig


bc = BaseConfig()


class DBConfig(BaseConfig):
    DB_DRIVER: str = Field(..., env=f"{bc.DB_DIALECT}_DRIVER")
    DB_USER: str = Field(..., env=f"{bc.DB_DIALECT}_USER")
    DB_PASS: str = Field(..., env=f"{bc.DB_DIALECT}_PASS")
    DB_HOST: str = Field(..., env=f"{bc.DB_DIALECT}_HOST")
    DB_PORT: int = Field(..., env=f"{bc.DB_DIALECT}_PORT")
    DB_NAME: str = Field(..., env=f"{bc.DB_DIALECT}_NAME")
    DB_URL: str = ""

    RANKINGS: dict = {}
    MATCHES: Dict[str, Dict[str, str]] = {}

    @validator("DB_URL")
    def _db_url_value(cls, db_url, values) -> str:
        return (
            f"{values['DB_DIALECT']}+{values['DB_DRIVER']}://"
            + f"{values['DB_USER']}:{values['DB_PASS']}@"
            + f"{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        )

    @validator("RANKINGS")
    def _load_rankings(cls, rankings, values) -> dict:
        return cls.read_json(values["RANKINGS_FILE"])

    @validator("MATCHES")
    def _load_matches(cls, matches, values) -> Dict[str, Dict[str, str]]:
        return cls.read_json(
            values["MATCHES_FILE"],
            lambda d: {(None if not k else k): v for k, v in d.items()},
        )
