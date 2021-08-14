from contextlib import closing
from typing import Any, Dict, List, Tuple

import typer
from sqlalchemy.orm import Session
from typer.colors import CYAN, GREEN

from config import crwc, qsc, shac, thec, wikic
from rankr import crawlers as c, db_models as d, repos as r
from utils import csv_export


def engine_select(engine: str) -> Tuple[Any, Any]:
    """Returns the Crawler & the Config classes for the selected engine.

    Args:
        engine (str): The specified engine

    Raises:
        ValueError: If engine is not supported

    Returns:
        Tuple[Any, Any]: The engines' Crawler & Config classes
    """
    crawler_configs = [qsc, shac, thec, wikic]
    crawler_classes = [
        c.QSCrawler,
        c.ShanghaiCrawler,
        c.THECrawler,
        c.WikipediaCrawler,
    ]
    engines = zip(crwc.SUPPORTED_ENGINES, zip(crawler_configs, crawler_classes))
    for e in engines:
        if e[0] == engine:
            return e[1]
    raise typer.BadParameter(
        f"Wrong engine value '{engine}'. "
        + f"Only {crwc.SUPPORTED_ENGINES} are supported."
    )


def engine_check(value: str) -> List[str]:
    value = value.lower()
    if value == "all":
        return crwc.SUPPORTED_ENGINES
    if value == "rankings":
        return crwc.SUPPORTED_ENGINES[:-1]
    return [value]


def get_wikipedia_urls() -> List[Dict[str, str]]:
    """Retrieves the list of Wikipedia URLS for ranked institutions."""
    db: Session
    with closing(d.SessionLocal()) as db:
        query = (d.Institution.grid_id, d.Institution.wikipedia_url)
        institutions = (
            db.query(*query).join(d.Institution.rankings).group_by(*query).all()
        )
    return [institution._asdict() for institution in institutions]


def crawl(
    engines: str = typer.Argument(..., callback=engine_check),
    commit: bool = typer.Option(True, help="Commit the results to the DB?"),
):
    """Crawls the ranking websites and commits the results to DB

    Engine values: qs, shanghai, the

    Special engine value: all = [qs, shanghai, the, wikipedia]

    Special engine value: rankings = [qs, shanghai, the]

    Args:
        engines (List[str]): The selected engines used for crawling
        commit (bool): Whether or not commit the ranking table to DB
    """
    all_not_matched = []
    all_fuzzy_matched = []
    for engine in engines:
        typer.secho(f"Processing {engine} urls.", fg=CYAN)
        config, crawler = engine_select(engine)
        if engine == "wikipedia":
            # The WikipediaCrawler class works a little different.
            urls = get_wikipedia_urls() or config.URLS
            for url in urls:
                w = crawler(url["grid_id"], url["wikipedia_url"])
                w.crawl()
            continue

        with closing(d.SessionLocal()) as db:
            institution_repo = r.InstitutionRepo(db)
            soup = {}  # Group soup by country for better performance.
            for inst in institution_repo.get_db_institutions(limit=0):
                try:
                    soup[inst.country.country][inst.soup] = inst.grid_id
                except KeyError:
                    soup[inst.country.country] = {inst.soup: inst.grid_id}

            for page in config.URLS:
                if not page.get("crawl"):
                    continue

                ranking_info = {
                    "ranking_system": page["ranking_system"],
                    "ranking_type": page["ranking_type"],
                    "year": page["year"],
                    "field": page["field"],
                    "subject": page["subject"],
                }

                print("Processing:", " ".join(map(str, ranking_info.values())))

                p = crawler(url=page["url"], **ranking_info)
                matched, not_matched, fuzzy_matched = p.crawl_and_process(
                    institution_repo=institution_repo, soup=soup
                )
                if commit:
                    db.add_all(matched)
                    db.commit()
                all_fuzzy_matched.extend(fuzzy_matched)
                all_not_matched.extend(not_matched)

    if all_fuzzy_matched:
        csv_export(crwc.DATA_DIR / "fuzz.csv", all_fuzzy_matched)
        typer.echo("Saved the list of fuzzy-matched institutions.")
    if all_not_matched:
        csv_export(crwc.DATA_DIR / "not_mached.csv", all_not_matched)
        typer.echo("Saved the list of not matched institutions.")

    typer.secho("All done!", fg=GREEN)
