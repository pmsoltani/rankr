from pydantic import validator

from config.base_config import BaseConfig


class DBConfig(BaseConfig):
    DB_URL: str = ""

    MATCHES: dict[str, dict[str, str]] = {}

    @validator("DB_URL", always=True)
    def _db_url_value(cls, db_url, values) -> str:
        db_path = values["DATA_DIR"] / "rankr.sqlite"
        return f"sqlite:///{db_path.as_posix()}"

    @validator("MATCHES")
    def _load_matches(cls, matches, values) -> dict[str, dict[str, str]]:
        return cls.read_json(
            values["MATCHES_FILE"],
            lambda d: {(None if not k else k): v for k, v in d.items()},
        )
