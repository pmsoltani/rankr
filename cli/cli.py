import typer

from cli.commands import cmd_crawl, cmd_db


cli = typer.Typer()
cli.command(name="crawl")(cmd_crawl.crawl)
cli.add_typer(cmd_db.cli, name="db")
