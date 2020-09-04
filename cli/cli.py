import typer

from cli.commands import cmd_crawl, cmd_db, cmd_test


cli = typer.Typer()
cli.command(name="crawl")(cmd_crawl.crawl)
cli.command(name="cov")(cmd_test.cov)
cli.command(name="test")(cmd_test.test)
cli.add_typer(cmd_db.cli, name="db")
