import typer

from cli.commands.db import db_init


cli = typer.Typer()
cli.command(name="init")(db_init.init)
