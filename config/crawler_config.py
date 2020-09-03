from pathlib import Path
from typing import Dict, List

from pydantic import Field, HttpUrl, validator

from config.base_config import BaseConfig
from config.db_config import dbc


class CrawlerConfig(BaseConfig):
    USER_AGENT: str = Field(..., env="USER_AGENT")
    HEADERS: Dict[str, str] = {}

    @validator("HEADERS")
    def _headers_value(cls, headers, values) -> Dict[str, str]:
        return {"User-Agent": values["USER_AGENT"]}

    DOWNLOAD_DIR: Path = Path()
    SUPPORTED_ENGINES: List[str] = list(dbc.RANKINGS["metrics"]) + ["wikipedia"]


class QSConfig(CrawlerConfig):
    BASE_URL: HttpUrl = Field("https://www.topuniversities.com/")
    URLS: List[dict] = []

    @validator("URLS")
    def _load_urls(cls, urls, values) -> List[dict]:
        return cls.read_json(values["QS_URLS_FILE"])

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["MAIN_DIR"] / values["DATA_DIR"] / "qs"

    FIELDS: Dict[str, str] = {
        "rank": "Rank",
        "# rank": "Rank",
        "university": "Institution",
        "url": "URL",
        "location": "Country",
        "overall score": "Overall Score",
        "academic reputation": "Academic Reputation",
        "employer reputation": "Employer Reputation",
        "faculty student": "Faculty Student",
        "international faculty": "International Faculty",
        "international students": "International Students",
        "citations per faculty": "Citations per Faculty",
        "h-index citations": "H-index Citations",
        "citations per paper": "Citations per Paper",
    }


class ShanghaiConfig(CrawlerConfig):
    BASE_URL: HttpUrl = Field("http://www.shanghairanking.com/")
    URLS: List[dict] = []

    @validator("URLS")
    def _load_urls(cls, urls, values) -> List[dict]:
        return cls.read_json(values["SHANGHAI_URLS_FILE"])

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["MAIN_DIR"] / values["DATA_DIR"] / "shanghai"

    FIELDS: Dict[str, str] = {
        "world rank": "Rank",
        "url": "URL",
        "national/regionalrank": "National Rank",
        "national/regional rank": "National Rank",
        "total score": "Total Score",
        "alumni": "Alumni",
        "award": "Award",
        "hici": "HiCi",
        "n&s": "N&S",
        "pub": "PUB",
        "pcp": "PCP",
        "cnci": "CNCI",
        "ic": "IC",
        "top": "TOP",
        "q1": "Q1",
    }


class THEConfig(CrawlerConfig):
    BASE_URL: HttpUrl = Field("https://www.timeshighereducation.com/")
    URLS: List[dict] = []

    @validator("URLS")
    def _load_urls(cls, urls, values) -> List[dict]:
        return cls.read_json(values["THE_URLS_FILE"])

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["MAIN_DIR"] / values["DATA_DIR"] / "the"

    FIELDS: Dict[str, str] = {
        "rank": "Rank",
        "name": "Institution",
        "scores_overall": "Overall",
        "scores_teaching": "Teaching",
        "scores_research": "Research",
        "scores_citations": "Citations",
        "scores_industry_income": "Industry Income",
        "scores_international_outlook": "International Outlook",
        "url": "URL",
        "location": "Country",
        "stats_number_students": "No. of FTE Students",
        "stats_student_staff_ratio": "No. of Students per Staff",
        "stats_pc_intl_students": "International Students",
        "stats_female_male_ratio": "Female:Male Ratio",
    }


class WikipediaConfig(CrawlerConfig):
    BASE_URL: HttpUrl = Field("https://en.wikipedia.org/")

    @validator("DOWNLOAD_DIR")
    def _download_dir_value(cls, download_dir, values) -> Path:
        return values["MAIN_DIR"] / values["DATA_DIR"] / "wikipedia"


crwc = CrawlerConfig()
qsc = QSConfig()
shac = ShanghaiConfig()
thec = THEConfig()
wikic = WikipediaConfig()
