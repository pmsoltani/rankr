import enum
from pathlib import Path
from typing import Any, Callable

from pydantic import field_validator

from config.meta import ProjectMeta
from utils.get_json import get_json


class BackendEnvEnum(str, enum.Enum):
    dev = "dev"
    prod = "prod"
    test = "test"


class BaseConfig(ProjectMeta):
    BACKEND_ENV: BackendEnvEnum = BackendEnvEnum.dev

    ROOT_DIR: Path = Path.cwd()
    BACKEND_DIR: Path = ROOT_DIR / ProjectMeta().BACKEND_NAME
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

    @field_validator(
        "BACKEND_DIR",
        "DATA_DIR",
        "ESSENTIALS_DIR",
        "GRID_DATABASE_DIR",
        "RESPONSES_DIR",
    )
    @classmethod
    def _ensure_dir_exists(cls, directory: Path) -> Path:
        if not directory.exists():
            raise FileNotFoundError(directory)
        return directory

    @field_validator(
        "COUNTRIES_FILE",
        "COUNTRY_NAMES_FILE",
        "MATCHES_FILE",
        "RANKINGS_FILE",
        "QS_URLS_FILE",
        "SHANGHAI_URLS_FILE",
        "THE_URLS_FILE",
    )
    @classmethod
    def _ensure_file_exists(cls, file: Path) -> Path:
        if not file.exists():
            raise FileNotFoundError(file)
        return file

    @classmethod
    def read_json(
        cls,
        file_path: Path | str,
        object_hook: Callable[..., Any] | None = None,
    ):
        return get_json(file_path=file_path, object_hook=object_hook)
