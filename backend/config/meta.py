import tomllib
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseSettings


def _get_project_meta() -> Dict[str, Any]:
    with open(Path.cwd() / "pyproject.toml", "rb") as pyproject:
        return tomllib.load(pyproject)["project"]


meta = _get_project_meta()


class ProjectMeta(BaseSettings):
    BACKEND_NAME: str = meta["name"]

    DESCRIPTION = meta["description"]
    AUTHORS = [author["name"] for author in meta["authors"]]
    VERSION = meta["version"]
