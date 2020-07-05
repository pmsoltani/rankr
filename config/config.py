from pathlib import Path

from environs import Env


env = Env()
env.read_env()

APP_ENV = env("APP_ENV", "development")


class BaseConfig(object):
    DATA_DIR = env("DATA_DIR", "data")
    MAIN_DIR = Path.cwd() / DATA_DIR

    USER_AGENT = env("USER_AGENT")


class ShanghaiConfig(BaseConfig):
    BASE = env("SHANGHAI_BASE")
    URL = env("SHANGHAI_URL")
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
