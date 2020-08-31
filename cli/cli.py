import typer

from cli.commands import cmd_crawl


cli = typer.Typer()
cli.add_typer(cmd_crawl.cli, name="crawl")
