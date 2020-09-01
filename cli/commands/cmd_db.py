import typer

from cli.commands.db import db_grid, db_init


cli = typer.Typer()
cli.command(name="init")(db_init.db_init)
cli.command(name="grid")(db_grid.db_grid)
