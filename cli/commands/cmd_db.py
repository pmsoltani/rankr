import typer

from cli.commands.db import db_grid, db_init, db_rankings


cli = typer.Typer()
cli.command(name="init")(db_init.db_init)
cli.command(name="grid")(db_grid.db_grid)
cli.command(name="rankings")(db_rankings.db_rankings)


@cli.command()
def reset(
    ctx: typer.Context,
    confirm: bool = typer.Option(
        ...,
        prompt="You're about to drop the database and re-create it. Continue?",
        confirmation_prompt=True,
    ),
):
    if not confirm:
        raise typer.Abort()
    ctx.invoke(db_init.db_init, force=True)
    ctx.invoke(db_grid.db_grid)
    ctx.invoke(db_rankings.db_rankings)
