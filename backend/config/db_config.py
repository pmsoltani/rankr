from typing import Dict, Optional

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
    DB_ENCODING: Optional[str]

    MATCHES: Dict[str, Dict[str, str]] = {}

    @validator("DB_URL")
    def _db_url_value(cls, db_url, values) -> str:
        return (
            f"{values['DB_DIALECT']}+{values['DB_DRIVER']}://"
            + f"{values['DB_USER']}:{values['DB_PASS']}@"
            + f"{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        )

    @validator("DB_ENCODING", always=True)
    def _db_encoding_value(cls, db_encoding, values) -> str:
        return "utf8mb4" if values["DB_DIALECT"] == "mysql" else "utf8"

    @validator("MATCHES")
    def _load_matches(cls, matches, values) -> Dict[str, Dict[str, str]]:
        return cls.read_json(
            values["MATCHES_FILE"],
            lambda d: {(None if not k else k): v for k, v in d.items()},
        )
