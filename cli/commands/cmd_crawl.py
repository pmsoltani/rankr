from typing import Any, Dict, List, Tuple

import typer
from sqlalchemy.orm.session import Session
from typer.colors import CYAN, GREEN

from config import (
    CrawlerConfig,
    QSConfig,
    ShanghaiConfig,
    THEConfig,
    WikipediaConfig,
)
from crawlers import QSCrawler, ShanghaiCrawler, THECrawler, WikipediaCrawler
from rankr.db_models import Institution, SessionLocal


def engine_select(engine: str) -> Tuple[Any, Any]:
    if engine == "qs":
        return (QSConfig, QSCrawler)
    if engine == "shanghai":
        return (ShanghaiConfig, ShanghaiCrawler)
    if engine == "the":
        return (THEConfig, THECrawler)
    if engine == "wikipedia":
        return (WikipediaConfig, WikipediaCrawler)
    raise ValueError


def engine_check(values: List[str]) -> List[str]:
    for value in values:
        if value.lower() not in CrawlerConfig.SUPPORTED_ENGINES:
            raise typer.BadParameter(
                f"Wrong engine value '{value}'. "
                + f"Only {CrawlerConfig.SUPPORTED_ENGINES} are supported."
            )
    return [v.lower() for v in values]


def get_wikipedia_urls() -> List[Dict[str, str]]:
    try:
        db: Session = SessionLocal()
        query = (Institution.grid_id, Institution.wikipedia_url)
        institutions = (
            db.query(*query).join(Institution.rankings).group_by(*query).all()
        )
    finally:
        db.close()
    return [institution._asdict() for institution in institutions]


def crawl(engines: List[str] = typer.Argument(..., callback=engine_check)):
    for engine in engines:
        typer.secho(f"Processing {engine} urls.", fg=CYAN)
        config, crawler = engine_select(engine)
        if engine == "wikipedia":
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
