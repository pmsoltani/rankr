from pathlib import Path

import typer
from sqlalchemy.schema import CreateTable

from cli.commands.db import db_crosswalk, db_init, db_ror
from rankr import db_models as d


cli = typer.Typer()
cli.command(name="init")(db_init.db_init)
cli.command(name="ror")(db_ror.db_ror)
cli.command(name="crosswalk")(db_crosswalk.db_crosswalk)


@cli.command()
def schema(output: Path = typer.Argument(Path("schema.sql"))):
    """Emits the CREATE TABLE DDL (SQLite dialect) to a file.

    This is the canonical schema for the downstream Cloudflare D1 database.
    """
    statements = [
        str(CreateTable(table).compile(d.engine)).strip() + ";"
        for table in d.Base.metadata.sorted_tables
    ]
    output.write_text("\n\n".join(statements) + "\n")
    typer.secho(f"Wrote schema to {output}", fg=typer.colors.GREEN)


@cli.command()
def reset(
    ctx: typer.Context,
    confirm: bool = typer.Option(
        ...,
        prompt="You're about to drop the database and re-create it. Continue?",
        confirmation_prompt=True,
    ),
):
    """Executes all "db" commands in sequence.

    Args:
        ctx (typer.Context): The command context
        confirm (bool): User's confirmation for destructive operation

    Raises:
        typer.Abort: If the user does not confirm the operation
    """
    if not confirm:
        raise typer.Abort()
    ctx.invoke(db_init.db_init, drop=True)
    ctx.invoke(db_ror.db_ror)
