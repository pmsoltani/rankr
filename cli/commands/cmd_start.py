import subprocess

import typer

from config import appc


def start(
    reload: bool = typer.Option(False, help="Enable auto-reload?")
) -> int:
    """Starts the rankr webserver."""
    reload_flag = "" if not reload else "--reload"
    cmd = (
        "uvicorn main:app "
        + f"--host {appc.APP_HOST} --port {appc.APP_PORT} {reload_flag}"
    )
    return subprocess.call(args=cmd, shell=True)
