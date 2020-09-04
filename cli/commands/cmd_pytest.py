import subprocess
from pathlib import Path

import typer

from config import appc


def test(
    path: Path = typer.Argument(appc.ROOT_DIR),
    capture: bool = typer.Option(True, help="Disable print statements?"),
) -> int:
    """Runs unit tests with pytest.

    Args:
        path (Path, optional): Test path. Defaults to root directory.
        capture (bool, optional): Whether to suppress print statements
        or not. Defaults to True.

    Returns:
        int: The return code of the command
    """
    capture_flag = "" if capture else "--capture=no"
    cmd = f"pytest {capture_flag} {path}"
    return subprocess.call(args=cmd, shell=True)


def cov(path: Path = typer.Argument(appc.ROOT_DIR)) -> int:
    """Runs a test coverage report.

    Args:
        path (Path, optional): Test coverage analysis path. Defaults to
        root directory

    Returns:
        int: The return code of the command
    """
    cmd = f"pytest --cov-report term-missing --cov {path}"
    return subprocess.call(args=cmd, shell=True)
