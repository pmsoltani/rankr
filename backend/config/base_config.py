import enum
from pathlib import Path
from typing import Callable, Union

from pydantic import Field, validator

from config.meta import ProjectMeta
from utils.get_json import get_json


class DialectEnum(str, enum.Enum):
    mysql = "mysql"
    postgresql = "postgresql"


class BackendEnvEnum(str, enum.Enum):
    dev = "dev"
    prod = "prod"
    test = "test"


class BaseConfig(ProjectMeta):
    BACKEND_ENV: BackendEnvEnum = BackendEnvEnum.dev

    ROOT_DIR: Path = Path.cwd()
    BACKEND_DIR: Path = ROOT_DIR / ProjectMeta().BACKEND_NAME
    MIGRATIONS_DIR: Path = BACKEND_DIR / "migrations"
    DATA_DIR: Path = ROOT_DIR / "data"
    ESSENTIALS_DIR: Path = ROOT_DIR / "essentials"
    RESPONSES_DIR: Path = DATA_DIR / "responses"

    COUNTRIES_FILE: Path = ESSENTIALS_DIR / "countries.csv"
    COUNTRY_NAMES_FILE: Path = ESSENTIALS_DIR / "country_names.json"
    MATCHES_FILE: Path = ESSENTIALS_DIR / "matches.json"
    RANKINGS_FILE: Path = ESSENTIALS_DIR / "rankings.json"

    QS_URLS_FILE: Path = ESSENTIALS_DIR / "qs_urls.json"
    SHANGHAI_URLS_FILE: Path = ESSENTIALS_DIR / "shanghai_urls.json"
    THE_URLS_FILE: Path = ESSENTIALS_DIR / "the_urls.json"

    GRID_DATABASE_DIR: Path = DATA_DIR / "grid" / "full_tables"

    DB_DIALECT: DialectEnum = Field(..., env="DB_DIALECT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator(
        "BACKEND_DIR",
        "MIGRATIONS_DIR",
        "DATA_DIR",
        "ESSENTIALS_DIR",
        "GRID_DATABASE_DIR",
        "RESPONSES_DIR",
    )
    def _ensure_dir_exists(cls, directory: Path) -> Path:
        if not directory.exists():
            raise FileNotFoundError(directory)
        return directory

    @validator(
        "COUNTRIES_FILE",
        "COUNTRY_NAMES_FILE",
        "MATCHES_FILE",
        "RANKINGS_FILE",
        "QS_URLS_FILE",
        "SHANGHAI_URLS_FILE",
        "THE_URLS_FILE",
    )
    def _ensure_file_exists(cls, file: Path) -> Path:
        if not file.exists():
            raise FileNotFoundError(file)
        return file

    @classmethod
    def read_json(
        cls, file_path: Union[Path, str], object_hook: Callable = None
    ):
        return get_json(file_path=file_path, object_hook=object_hook)
