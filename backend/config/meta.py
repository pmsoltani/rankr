from pathlib import Path
from typing import Any, Dict

import toml
from pydantic import BaseSettings


def _get_project_meta() -> Dict[str, Any]:
    with open(Path.cwd() / "pyproject.toml") as pyproject:
        file_contents = pyproject.read()
    return toml.loads(file_contents)["tool"]["poetry"]


meta = _get_project_meta()


class ProjectMeta(BaseSettings):
    APP_NAME: str = meta["name"]

    DESCRIPTION = meta["description"]
    AUTHORS = meta["authors"]
    VERSION = meta["version"]
