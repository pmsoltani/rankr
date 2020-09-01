import typer

from cli.commands.db import db_grid, db_init, db_rankings


cli = typer.Typer()
cli.command(name="init")(db_init.db_init)
cli.command(name="grid")(db_grid.db_grid)
cli.command(name="rankings")(db_rankings.db_rankings)
