from typing import List, Optional, Union

from pydantic import AnyHttpUrl, validator

from config.base_config import BaseConfig


class APPConfig(BaseConfig):
    GRID_ID_PATTERN: str = r"grid\.[0-9]{4,6}\.[0-9a-f]{1,2}"

    API_V1_STR: str = "/api/v1"
    APP_HOST: str
    APP_PORT: int
    APP_TLD: Optional[AnyHttpUrl] = None
    CORS_ORIGINS: Union[str, List[AnyHttpUrl]]

    ENTITIES: dict = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("APP_TLD")
    def _app_tld_value(cls, app_tld, values) -> str:
        return f"http://{values['APP_HOST']}:{values['APP_PORT']}"

    @validator("CORS_ORIGINS", pre=True)
    def _assemble_cors_origins(cls, cors_origins):
        if isinstance(cors_origins, str):
            return [item.strip() for item in cors_origins.split(",")]
        return cors_origins

    @validator("ENTITIES")
    def _load_entities(cls, entities, values) -> str:
        return cls.read_json(values["ENTITIES_FILE"])
