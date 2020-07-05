from pathlib import Path

from environs import Env


env = Env()
env.read_env()

APP_ENV = env("APP_ENV", "development")


class BaseConfig(object):
    DATA_DIR = env("DATA_DIR", "data")
    MAIN_DIR = Path.cwd() / DATA_DIR

    USER_AGENT = env("USER_AGENT")
