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
