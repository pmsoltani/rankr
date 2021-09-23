import subprocess

import typer

from config import backc


def start(
    reload: bool = typer.Option(False, help="Enable auto-reload?")
) -> int:
    """Starts the rankr webserver."""
    reload_flag = "" if not reload else "--reload"
    cmd = (
        f"uvicorn {backc.BACKEND_NAME}.api.server:app "
        + f"--host {backc.BACKEND_HOST} --port {backc.BACKEND_PORT} "
        + reload_flag
    )
    return subprocess.call(args=cmd, shell=True)
