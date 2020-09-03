from typing import Optional

from pydantic import AnyHttpUrl, Field, validator

from config.base_config import BaseConfig


class APPConfig(BaseConfig):
    GRID_ID_PATTERN: str = r"grid\.[0-9]{4,6}\.[0-9a-f]{1,2}"

    APP_ENV: str = Field("development", env="APP_ENV")
    APP_NAME: str = Field(..., env="APP_NAME")
    API_V1_STR: str = Field("", env="API_V1_STR")
    APP_HOST: str = Field(..., env="APP_HOST")
    APP_PORT: int = Field(..., env="APP_PORT")
    APP_TLD: Optional[AnyHttpUrl] = None

    ENTITIES: dict = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("APP_TLD")
    def _app_tld_value(cls, app_tld, values) -> str:
        return f"http://{values['APP_HOST']}:{values['APP_PORT']}"

    @validator("ENTITIES")
    def _load_entities(cls, entities, values) -> str:
        return cls.read_json(values["ENTITIES_FILE"])


appc = APPConfig()
