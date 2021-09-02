from contextlib import closing

import typer

from rankr import crawlers as c, db_models as d, repos as r


def db_grid():
    """Populates the database with country & GRID data."""
    try:
        with closing(d.SessionLocal()) as db:
            country_repo = r.CountryRepo(db)
            institution_repo = r.InstitutionRepo(db)
            grid_crawler = c.GRIDCrawler(country_repo, institution_repo)
            grid_crawler.crawl()
    except Exception as exc:
        typer.secho(
            "Error populating the database: {type(exc)}", fg=typer.colors.RED
        )
        typer.secho(str(exc), fg=typer.colors.CYAN)
        raise typer.Abort()
