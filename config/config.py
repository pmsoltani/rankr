import json
from pathlib import Path
from typing import List

from environs import Env


env = Env()
env.read_env()

APP_ENV = env("APP_ENV", "development")


class BaseConfig(object):
    DATA_DIR = env("DATA_DIR", "data")
    MAIN_DIR = Path.cwd() / DATA_DIR

    USER_AGENT = env("USER_AGENT")

    CRAWLER_ENGINE = env.list("CRAWLER_ENGINE", ["QS", "Shanghai", "THE"])

    @classmethod
    def get_urls(cls, path: Path) -> List[dict]:
        with open(path, "r") as urls_file:
            url_list = json.loads(urls_file.read())
        return url_list


class ShanghaiConfig(BaseConfig):
    headers = {"User-Agent": BaseConfig.USER_AGENT}
    BASE_URL = env("SHANGHAI_BASE")
    _raw_urls = env("SHANGHAI_URLS_FILE", "shanghai_urls.json")
    URLS = BaseConfig.get_urls(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR = BaseConfig.MAIN_DIR / "Shanghai"

    FIELDS = {
        "World Rank": "Rank",
        "URL": "URL",
        "Institution*": "University",
        "Institution": "University",
        "Country/Region": "Country",
        "Country /Region": "Country",
        "Country / Region": "Country",
        "By location": "Country",
        "National/RegionalRank": "National Rank",
        "National/Regional Rank": "National Rank",
        "Total Score": "Total Score",
    }


class THEConfig(BaseConfig):
    headers = {"User-Agent": BaseConfig.USER_AGENT}
    BASE_URL = env("THE_BASE")
    _raw_urls = env("THE_URLS_FILE", "the_urls.json")
    URLS = BaseConfig.get_urls(Path.cwd() / _raw_urls)

    DOWNLOAD_DIR = BaseConfig.MAIN_DIR / "THE"

    FIELDS = {
        "Rank": "Rank",
        "URL": "URL",
        "Overall": "Overall",
        "Teaching": "Teaching",
        "Research": "Research",
        "Citations": "Citations",
        "Industry Income": "Industry Income",
        "International Outlook": "International Outlook",
        "No. of FTE Students": "No. of FTE Students",
        "No. of students per staff": "No. of students per staff",
        "International Students": "International Students",
        "Female:Male Ratio": "Female:Male Ratio",
        "Overall": "Overall",
        "Teaching": "Teaching",
        "Research": "Research",
        "Citations": "Citations",
        "Industry Income": "Industry Income",
        "International Outlook": "International Outlook",
    }
