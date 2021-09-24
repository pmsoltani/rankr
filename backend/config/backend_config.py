from typing import List, Union

from pydantic import AnyHttpUrl, validator

from config.base_config import BaseConfig


class BackendConfig(BaseConfig):
    GRID_ID_PATTERN: str = r"grid\.[0-9]{4,6}\.[0-9a-f]{1,2}"

    API_V1_STR: str = "/api/v1"
    BACKEND_HOST: str
    BACKEND_PORT: int
    CORS_ORIGINS: Union[str, List[AnyHttpUrl]]

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    REDIS_DB: str
    REDIS_URL: str = ""
    REDIS_ENCODING: str = "utf8"
    REDIS_CACHE_EXPIRES_AFTER: int = 2592000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("CORS_ORIGINS", pre=True)
    def _assemble_cors_origins(cls, cors_origins):
        if isinstance(cors_origins, str):
            return [item.strip() for item in cors_origins.split(",")]
        return cors_origins

    @validator("REDIS_URL", always=True)
    def _db_url_value(cls, redis_url, values) -> str:
        return (
            "redis://:"
            + f"{values['REDIS_PASS']}@"
            + f"{values['REDIS_HOST']}:{values['REDIS_PORT']}"
            + f"/{values['REDIS_DB']}"
        )
