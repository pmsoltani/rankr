import typer

from cli.commands import cmd_crawl, cmd_db


cli = typer.Typer()
cli.add_typer(cmd_crawl.cli, name="crawl")
cli.add_typer(cmd_db.cli, name="db")
