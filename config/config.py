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


class ShanghaiConfig(BaseConfig):
    BASE_URL = env("SHANGHAI_BASE")
    _raw_urls = env("SHANGHAI_URLS_FILE", "shanghai_urls.json")

    with open(Path.cwd() / _raw_urls, "r") as urls_file:
        URLS: List[dict] = json.loads(urls_file.read())

    FIELDS = {
        "World Rank": "Rank",
        "URL": "URL",
        "Institution*": "University",
        "Institution": "University",
        "Country/Region": "Country",
        "By location": "Country",
        "National/RegionalRank": "National Rank",
        "National/Regional Rank": "National Rank",
        "Total Score": "Total Score",
    }
