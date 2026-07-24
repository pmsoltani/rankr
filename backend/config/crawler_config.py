from pathlib import Path
from typing import Any, ClassVar

from pydantic import Field, ValidationInfo, field_validator

from config.base_config import BaseConfig
from config.db_config import DBConfig
from utils import get_row


dbc = DBConfig()


class CrawlerConfig(BaseConfig):
    USER_AGENT: str = (
        "USER_AGENT=Mozilla/5.0 "
        + "(Macintosh; Intel Mac OS X 10_10_1) "
        + "AppleWebKit/537.36 "
        + "(KHTML, like Gecko) "
        + "Chrome/39.0.2171.95 "
        + "Safari/537.36"
    )
    HEADERS: dict[str, str] = Field(default_factory=dict)

    DOWNLOAD_DIR: Path = Path()

    EXCLUSIONS: list[str] = Field(default_factory=list)
    COUNTRY_NAMES: dict[str, str] = Field(default_factory=dict)
    COUNTRIES: dict[str, dict[str, str]] = Field(default_factory=dict)

    RANKINGS: dict[str, Any] = Field(default_factory=dict)
    SUPPORTED_ENGINES: list[str] = Field(default_factory=list)

    @field_validator("HEADERS")
    @classmethod
    def _headers_value(cls, headers, info: ValidationInfo) -> dict[str, str]:
        return {"User-Agent": info.data["USER_AGENT"]}

    @field_validator("EXCLUSIONS")
    @classmethod
    def _load_exclusions(cls, exclusions, info: ValidationInfo):
        return cls.read_json(info.data["EXCLUSIONS_FILE"])

    @field_validator("COUNTRY_NAMES")
    @classmethod
    def _load_country_names(cls, country_names, info: ValidationInfo):
        return cls.read_json(info.data["COUNTRY_NAMES_FILE"])

    @field_validator("COUNTRIES")
    @classmethod
    def _load_countries(cls, countries):
        return {row["country"]: row for row in get_row(dbc.COUNTRIES_FILE)}

    @field_validator("RANKINGS")
    @classmethod
    def _load_rankings(cls, rankings, info: ValidationInfo) -> dict[str, Any]:
        return cls.read_json(info.data["RANKINGS_FILE"])

    @field_validator("SUPPORTED_ENGINES")
    @classmethod
    def _resolve_supported_engines(
        cls, supported_engines, info: ValidationInfo
    ) -> list[str]:
        return list(info.data["RANKINGS"]["metrics"]) + ["wikipedia"]


class QSConfig(CrawlerConfig):
    BASE_URL: str = "https://www.topuniversities.com/"
    URLS: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("URLS")
    @classmethod
    def _load_urls(cls, urls, info: ValidationInfo) -> list[dict[str, Any]]:
        return cls.read_json(info.data["QS_URLS_FILE"])

    @field_validator("DOWNLOAD_DIR")
    @classmethod
    def _download_dir_value(cls, download_dir, info: ValidationInfo) -> Path:
        return info.data["DATA_DIR"] / "qs"

    FIELDS: ClassVar[dict[str, str]] = {
        "rank": "rank",
        "# rank": "rank",
        "university": "institution",
        "url": "url",
        "location": "country",
        "overall score": "overall score",
        "academic reputation": "academic reputation",
        "employer reputation": "employer reputation",
        "faculty student": "faculty student",
        "faculty student ratio": "faculty student",
        "international faculty": "international faculty",
        "international faculty ratio": "international faculty",
        "international students": "international students",
        "international students ratio": "international students",
        "citations per faculty": "citations per faculty",
        "h-index citations": "h-index citations",
        "citations per paper": "citations per paper",
    }


class ShanghaiConfig(CrawlerConfig):
    BASE_URL: str = "http://www.shanghairanking.com/"
    URLS: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("URLS")
    @classmethod
    def _load_urls(cls, urls, info: ValidationInfo) -> list[dict[str, Any]]:
        return cls.read_json(info.data["SHANGHAI_URLS_FILE"])

    @field_validator("DOWNLOAD_DIR")
    @classmethod
    def _download_dir_value(cls, download_dir, info: ValidationInfo) -> Path:
        return info.data["DATA_DIR"] / "shanghai"

    FIELDS: ClassVar[dict[str, str]] = {
        "world rank": "rank",
        "url": "url",
        "national/regionalrank": "national rank",
        "national/regional rank": "national rank",
        "total score": "total score",
        "alumni": "alumni",
        "award": "award",
        "hici": "hici",
        "n&s": "n&s",
        "pub": "pub",
        "pcp": "pcp",
        "cnci": "cnci",
        "ic": "ic",
        "top": "top",
        "q1": "q1",
    }


class THEConfig(CrawlerConfig):
    BASE_URL: str = "https://www.timeshighereducation.com/"
    URLS: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("URLS")
    @classmethod
    def _load_urls(cls, urls, info: ValidationInfo) -> list[dict[str, Any]]:
        return cls.read_json(info.data["THE_URLS_FILE"])

    @field_validator("DOWNLOAD_DIR")
    @classmethod
    def _download_dir_value(cls, download_dir, info: ValidationInfo) -> Path:
        return info.data["DATA_DIR"] / "the"

    FIELDS: ClassVar[dict[str, str]] = {
        "rank": "rank",
        "name": "institution",
        "scores_overall": "overall",
        "scores_teaching": "teaching",
        "scores_research": "research",
        "scores_citations": "citations",
        "scores_industry_income": "industry income",
        "scores_international_outlook": "international outlook",
        "url": "url",
        "location": "country",
        "stats_number_students": "no. of fte students",
        "stats_student_staff_ratio": "no. of students per staff",
        "stats_pc_intl_students": "international students",
        "stats_female_male_ratio": "female:male ratio",
    }


class WikipediaConfig(CrawlerConfig):
    BASE_URL: str = "https://en.wikipedia.org/"
    URLS: list[dict[str, Any]] = Field(default_factory=list)

    ALLOWED_LOGO_FORMATS: ClassVar[list[str]] = [".svg", ".png"]

    @field_validator("DOWNLOAD_DIR")
    @classmethod
    def _download_dir_value(cls, download_dir, info: ValidationInfo) -> Path:
        return info.data["DATA_DIR"] / "wikipedia"
