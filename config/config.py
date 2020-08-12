import io
import json
from pathlib import Path
from typing import Callable

from environs import Env


env = Env()
env.read_env()

APP_ENV = env("APP_ENV", "development")


def read_json_config(path: Path, object_hook: Callable = None):
    with io.open(path, "r", encoding="utf-8") as json_file:
        return json.loads(json_file.read(), object_hook=object_hook)


class DBConfig(object):
    DATA_DIR = env("DATA_DIR", "data")
    MAIN_DIR = Path.cwd() / DATA_DIR

    DIALECT = env("DIALECT")
    with env.prefixed(f"{DIALECT.upper()}_"):
        _DRIVER = env("DRIVER")
        _USER = env("USER")
        _PASS = env("PASS")
        _HOST = env("HOST")
        _PORT = env("PORT")
        _NAME = env("NAME")
    DB_URI = f"{DIALECT}+{_DRIVER}://{_USER}:{_PASS}@{_HOST}:{_PORT}/{_NAME}"
    GRID_DATABASE_DIR = env.list(
        "GRID_DATABASE_DIR", ["data", "grid", "full_tables"]
    )
    GRID_DATABASE_DIR = Path.cwd().joinpath(*GRID_DATABASE_DIR)

    _rankings_file_path = env.path("RANKINGS_FILE_PATH", "rankings.json")
    RANKINGS: dict = read_json_config(_rankings_file_path)

    _matches_file_path = env.path("MATCHES_FILE_PATH", "matches.json")
    MATCHES: dict = read_json_config(
        _matches_file_path,
        lambda d: {(None if not k else k): v for k, v in d.items()},
    )

    _country_names_path = env("COUNTRY_NAMES", "country_names.json")
    COUNTRY_NAMES = read_json_config(_country_names_path)

    @classmethod
    def country_name_mapper(cls, country: str) -> str:
        return cls.COUNTRY_NAMES.get(
            country.strip().replace("-", " ").lower(), country
        )


class CrawlerConfig(object):
    DATA_DIR = env("DATA_DIR", "data")
    MAIN_DIR = Path.cwd() / DATA_DIR

    USER_AGENT = env("USER_AGENT")

    CRAWLER_ENGINE = env.list("CRAWLER_ENGINE", ["qs", "shanghai", "the"])
    _country_names_path = env("COUNTRY_NAMES", "country_names.json")
    COUNTRY_NAMES = read_json_config(_country_names_path)

    @classmethod
    def country_name_mapper(cls, country: str) -> str:
        return cls.COUNTRY_NAMES.get(
            country.strip().replace("-", " ").lower(), country
        )


class QSConfig(CrawlerConfig):
    headers = {"User-Agent": CrawlerConfig.USER_AGENT}
    BASE_URL = env("QS_BASE")
    _raw_urls = env("QS_URLS_FILE", "qs_urls.json")
    URLS = read_json_config(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR = CrawlerConfig.MAIN_DIR / "qs"

    FIELDS = {
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
    headers = {"User-Agent": CrawlerConfig.USER_AGENT}
    BASE_URL = env("SHANGHAI_BASE")
    _raw_urls = env("SHANGHAI_URLS_FILE", "shanghai_urls.json")
    URLS = read_json_config(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR = CrawlerConfig.MAIN_DIR / "shanghai"

    FIELDS = {
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
    headers = {"User-Agent": CrawlerConfig.USER_AGENT}
    BASE_URL = env("THE_BASE")
    _raw_urls = env("THE_URLS_FILE", "the_urls.json")
    URLS = read_json_config(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR = CrawlerConfig.MAIN_DIR / "the"

    FIELDS = {
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
