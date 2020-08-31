import typer

from typing import Any, List, Tuple
from config import (
    CrawlerConfig,
    QSConfig,
    ShanghaiConfig,
    THEConfig,
    WikipediaConfig,
)
from crawlers import QSCrawler, ShanghaiCrawler, THECrawler, WikipediaCrawler


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


cli = typer.Typer()


def engine_check(values: List[str]) -> List[str]:
    for cnt, value in enumerate(values):
        if value.lower() not in CrawlerConfig.SUPPORTED_ENGINES:
            raise typer.BadParameter(
                f" Only {CrawlerConfig.SUPPORTED_ENGINES} are supported. "
                + f"Got '{value}'."
            )
    return [v.lower() for v in values]


@cli.command()
def crawl(engines: List[str] = typer.Argument(..., callback=engine_check)):
    for engine in engines:
        typer.secho(f"Processing {engine} urls.", fg="green")
        config, crawler = engine_select(engine)
        if engine == "wikipedia":
            for url in config.URLS:
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
