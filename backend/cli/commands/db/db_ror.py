from contextlib import closing

import typer

from rankr import crawlers as c
from rankr import db_models as d
from rankr import repos as r


def db_ror():
    """Populates the database with country & ROR data."""
    try:
        with closing(d.SessionLocal()) as db:
            country_repo = r.CountryRepo(db)
            institution_repo = r.InstitutionRepo(db)
            ror_crawler = c.RORCrawler(country_repo, institution_repo)
            ror_crawler.crawl()
    except Exception as exc:
        typer.secho(f"Error populating the database: {type(exc)}", fg=typer.colors.RED)
        typer.secho(str(exc), fg=typer.colors.CYAN)
        raise typer.Abort()
