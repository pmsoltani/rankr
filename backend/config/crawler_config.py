from pathlib import Path
from typing import Dict, List

from pydantic import HttpUrl, Field, validator

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
    HEADERS: Dict[str, str] = {}

    DOWNLOAD_DIR: Path = Path()

    COUNTRY_NAMES: dict = {}
    COUNTRIES: Dict[str, Dict[str, str]] = {}

    RANKINGS: dict = {}
    SUPPORTED_ENGINES: List[str] = []

    @validator("HEADERS")
    def _headers_value(cls, headers, values) -> Dict[str, str]:
        return {"User-Agent": values["USER_AGENT"]}

    @validator("COUNTRY_NAMES")
    def _load_country_names(cls, country_names, values):
        return cls.read_json(values["COUNTRY_NAMES_FILE"])

    @validator("COUNTRIES")
    def _load_countries(cls, countries):
        return {row["country"]: row for row in get_row(dbc.COUNTRIES_FILE)}

    @validator("RANKINGS")
    def _load_rankings(cls, rankings, values) -> dict:
        return cls.read_json(values["RANKINGS_FILE"])

    @validator("SUPPORTED_ENGINES")
    def _resolve_supported_engines(cls, supported_engines, values) -> List[str]:
        return list(values["RANKINGS"]["metrics"]) + ["wikipedia"]


class QSConfig(CrawlerConfig):
    BASE_URL: HttpUrl = Field("https://www.topuniversities.com/")
    URLS: List[dict] = []

    @validator("URLS")
    def _load_urls(cls, urls, values) -> List[dict]:
        return cls.read_json(values["QS_URLS_FILE"])

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["DATA_DIR"] / "qs"

    FIELDS: Dict[str, str] = {
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
    BASE_URL: HttpUrl = Field("http://www.shanghairanking.com/")
    URLS: List[dict] = []

    @validator("URLS")
    def _load_urls(cls, urls, values) -> List[dict]:
        return cls.read_json(values["SHANGHAI_URLS_FILE"])

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["DATA_DIR"] / "shanghai"

    FIELDS: Dict[str, str] = {
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
    BASE_URL: HttpUrl = Field("https://www.timeshighereducation.com/")
    URLS: List[dict] = []

    @validator("URLS")
    def _load_urls(cls, urls, values) -> List[dict]:
        return cls.read_json(values["THE_URLS_FILE"])

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["DATA_DIR"] / "the"

    FIELDS: Dict[str, str] = {
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
    BASE_URL: HttpUrl = Field("https://en.wikipedia.org/")

    ALLOWED_LOGO_FORMATS: List[str] = [".svg", ".png"]

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["DATA_DIR"] / "wikipedia"
