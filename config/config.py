import csv
import io
import json
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Union

from environs import Env

from utils import get_row


env = Env()
env.read_env()


def read_json_config(file_path: Union[Path, str], object_hook: Callable = None):
    with io.open(file_path, "r", encoding="utf-8") as json_file:
        return json.loads(json_file.read(), object_hook=object_hook)


class APPConfig(object):
    DATA_DIR: str = env("DATA_DIR", "data")
    MAIN_DIR: Path = Path.cwd() / DATA_DIR

    GRID_ID_PATTERN = r"grid\.[0-9]{4,6}\.[0-9a-f]{1,2}"

    APP_ENV: str = env("APP_ENV", "development")
    APP_NAME: str = env("APP_NAME",)
    API_V1_STR: str = env("API_V1_STR", "")
    APP_HOST: str = env("APP_HOST")
    APP_PORT: int = env.int("APP_PORT")
    APP_TLD = f"http://{APP_HOST}:{APP_PORT}"
    _entities_file_path = env.path("ENTITIES_FILE_PATH", "entities.json")
    ENTITIES = read_json_config(_entities_file_path)
    _countries_file: str = env("COUNTRIES_FILE_PATH", "countries.csv")
    with io.open(MAIN_DIR / _countries_file, encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        COUNTRIES: Dict[str, str] = {}
        for row in reader:
            COUNTRIES[row["country_code"]] = row["country"]


class DBConfig(object):
    DATA_DIR: str = env("DATA_DIR", "data")
    MAIN_DIR: Path = Path.cwd() / DATA_DIR

    DIALECT: str = env("DIALECT")
    with env.prefixed(f"{DIALECT.upper()}_"):
        _DRIVER: str = env("DRIVER")
        _USER: str = env("USER")
        _PASS: str = env("PASS")
        _HOST: str = env("HOST")
        _PORT: str = env("PORT")
        _NAME: str = env("NAME")
    DB_URI = f"{DIALECT}+{_DRIVER}://{_USER}:{_PASS}@{_HOST}:{_PORT}/{_NAME}"
    _grid_database_dir: List[str] = env.list(
        "GRID_DATABASE_DIR", ["data", "grid", "full_tables"]
    )
    GRID_DATABASE_DIR: Path = Path.cwd().joinpath(*_grid_database_dir)

    _rankings_file_path: Path = env.path("RANKINGS_FILE_PATH", "rankings.json")
    RANKINGS: dict = read_json_config(_rankings_file_path)

    _matches_file_path: Path = env.path("MATCHES_FILE_PATH", "matches.json")
    MATCHES: dict = read_json_config(
        _matches_file_path,
        lambda d: {(None if not k else k): v for k, v in d.items()},
    )

    _country_names_path: Path = env.path("COUNTRY_NAMES", "country_names.json")
    COUNTRY_NAMES: dict = read_json_config(_country_names_path)

    @classmethod
    def country_name_mapper(cls, country: str) -> str:
        try:
            return cls.COUNTRY_NAMES.get(
                country.strip().replace("-", " ").lower(), country
            )
        except AttributeError:  # country is None
            return country


class CrawlerConfig(object):
    DATA_DIR: str = env("DATA_DIR", "data")
    MAIN_DIR: Path = Path.cwd() / DATA_DIR

    USER_AGENT: str = env("USER_AGENT")

    SUPPORTED_ENGINES: List[str] = list(DBConfig.RANKINGS["metrics"])
    SUPPORTED_ENGINES += ["wikipedia"]
    CRAWLER_ENGINE = env.list("CRAWLER_ENGINE", ["qs", "shanghai", "the"])
    _country_names_path: Path = env.path("COUNTRY_NAMES", "country_names.json")
    COUNTRY_NAMES = read_json_config(_country_names_path)

    @classmethod
    def country_name_mapper(cls, country: str) -> str:
        return cls.COUNTRY_NAMES.get(
            country.strip().replace("-", " ").lower(), country
        )


class QSConfig(CrawlerConfig):
    headers: Dict[str, str] = {"User-Agent": CrawlerConfig.USER_AGENT}
    BASE_URL: str = env("QS_BASE")
    _raw_urls: str = env("QS_URLS_FILE", "qs_urls.json")
    URLS: List[dict] = read_json_config(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR: Path = CrawlerConfig.MAIN_DIR / "qs"

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
    headers: Dict[str, str] = {"User-Agent": CrawlerConfig.USER_AGENT}
    BASE_URL: str = env("SHANGHAI_BASE")
    _raw_urls: str = env("SHANGHAI_URLS_FILE", "shanghai_urls.json")
    URLS: List[dict] = read_json_config(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR: Path = CrawlerConfig.MAIN_DIR / "shanghai"

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
    headers: Dict[str, str] = {"User-Agent": CrawlerConfig.USER_AGENT}
    BASE_URL: str = env("THE_BASE")
    _raw_urls: str = env("THE_URLS_FILE", "the_urls.json")
    URLS: List[dict] = read_json_config(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR: Path = CrawlerConfig.MAIN_DIR / "the"

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
    headers: Dict[str, str] = {"User-Agent": CrawlerConfig.USER_AGENT}
    BASE_URL: str = env("WIKIPEDIA_BASE")
    _raw_urls: Path = DBConfig.GRID_DATABASE_DIR / "institutes.csv"
    URLS: Iterator[Dict[str, str]] = get_row(_raw_urls)

    DOWNLOAD_DIR: Path = CrawlerConfig.MAIN_DIR / "wikipedia"
