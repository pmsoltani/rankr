import subprocess
from pathlib import Path

import typer

from config import backc


def flake8(path: Path = typer.Argument(backc.ROOT_DIR)) -> int:
    """Runs flake8 to analyze the code-base for linting issues.

    Args:
        path (Path, optional): The directory to analyze. Defaults to
        root directory.

    Returns:
        int: The return code of the command
    """
    cmd = f"flake8 {path}"
    return subprocess.call(args=cmd, shell=True)
