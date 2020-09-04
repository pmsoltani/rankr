import typer

from cli.commands import cmd_crawl, cmd_db, cmd_flake8, cmd_pytest, cmd_start


cli = typer.Typer()
cli.command(name="crawl")(cmd_crawl.crawl)

cli.command(name="flake8")(cmd_flake8.flake8)

cli.command(name="start")(cmd_start.start)

cli.command(name="cov")(cmd_pytest.cov)
cli.command(name="test")(cmd_pytest.test)

cli.add_typer(cmd_db.cli, name="db")
