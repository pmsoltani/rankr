from contextlib import closing
from typing import Any, Dict, List, Tuple

import typer
from sqlalchemy.orm.session import Session
from typer.colors import CYAN, GREEN

from config import crwc, qsc, shac, thec, wikic
from crawlers import QSCrawler, ShanghaiCrawler, THECrawler, WikipediaCrawler
from rankr.db_models import Institution, SessionLocal


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
    crawler_classes = [QSCrawler, ShanghaiCrawler, THECrawler, WikipediaCrawler]
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
    with closing(SessionLocal()) as db:
        query = (Institution.grid_id, Institution.wikipedia_url)
        institutions = (
            db.query(*query).join(Institution.rankings).group_by(*query).all()
        )
    return [institution._asdict() for institution in institutions]


def crawl(engines: str = typer.Argument(..., callback=engine_check)):
    """Crawls the target website using the selected engines.

    Engine values: qs, shanghai, the

    Special engine value: all = [qs, shanghai, the, wikipedia]

    Special engine value: rankings = [qs, shanghai, the]

    Args:
        engines (List[str]): The selected engines used for crawling
    """
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

        for page in config.URLS:
            if not page.get("crawl"):
                continue
            p = crawler(
                url=page["url"],
                year=page["year"],
                ranking_system=page["ranking_system"],
                ranking_type=page["ranking_type"],
                field=page["field"],
                subject=page["subject"],
            )
            p.crawl()

    typer.secho("All done!", fg=GREEN)
