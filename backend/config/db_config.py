from pydantic import Field, ValidationInfo, field_validator, model_validator

from config.base_config import BaseConfig


class DBConfig(BaseConfig):
    DB_URL: str = ""

    MATCHES: dict[str | None, dict[str, str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _set_db_url(self) -> "DBConfig":
        if not self.DB_URL:
            db_path = self.DATA_DIR / "rankr.sqlite"
            self.DB_URL = f"sqlite:///{db_path.as_posix()}"
        return self

    @field_validator("MATCHES")
    @classmethod
    def _load_matches(
        cls, matches: dict[str | None, dict[str, str]], info: ValidationInfo
    ) -> dict[str | None, dict[str, str]]:
        return cls.read_json(
            info.data["MATCHES_FILE"],
            lambda d: {(None if not k else k): v for k, v in d.items()},
        )
