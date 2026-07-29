import json
from typing import Any

import typer
from sqlalchemy import select

from config import crwc, qsc, shac, thec, wikic
from config import enums as e
from rankr import crawlers as c
from rankr import db_models as d
from rankr import repos as r
from utils import csv_export


def engine_select(engine: str) -> tuple[Any, Any]:
    """Returns the Crawler & the Config classes for the selected engine.

    Args:
        engine (str): The specified engine

    Raises:
        ValueError: If engine is not supported

    Returns:
        tuple[Any, Any]: The engines' Crawler & Config classes
    """
    crawler_configs = [qsc, shac, thec, wikic]
    crawler_classes = [
        c.QSCrawler,
        c.ShanghaiCrawler,
        c.THECrawler,
        c.WikipediaCrawler,
    ]
    engines = zip(crwc.SUPPORTED_ENGINES, zip(crawler_configs, crawler_classes))
    for name, config_and_crawler in engines:
        if name == engine:
            return config_and_crawler
    raise typer.BadParameter(
        f"Wrong engine value '{engine}'. "
        + f"Only {crwc.SUPPORTED_ENGINES} are supported."
    )


def engine_check(value: str) -> list[str]:
    value = value.lower()
    if value == "all":
        return crwc.SUPPORTED_ENGINES
    if value == "rankings":
        return crwc.SUPPORTED_ENGINES[:-1]
    return [value]


def get_wikipedia_urls() -> list[dict[str, str]]:
    """Retrieves the list of Wikipedia URLs for ranked institutions.

    The Wikipedia URL is stored as a `link` row (type=wikipedia), not on the
    institution itself, so we join through the links relationship.
    """
    stmt = (
        select(d.Institution.ror_id, d.Link.link.label("wikipedia_url"))
        .join(d.Institution.links)
        .join(d.Institution.rankings)
        .where(d.Link.type == e.LinkTypeEnum.wikipedia)
        .group_by(d.Institution.ror_id, d.Link.link)
    )
    with d.SessionLocal() as db:
        rows = db.execute(stmt).all()
    return [dict(row._mapping) for row in rows]


def crawl(
    engines: str = typer.Argument(..., callback=engine_check),
    commit: bool = typer.Option(True, help="Commit the results to the DB?"),
    offline: bool = typer.Option(False, help="Only use CSV files (no web crawling)."),
):
    """Crawls the ranking websites and commits the results to DB

    Engine values: qs, shanghai, the

    Special engine value: all = [qs, shanghai, the, wikipedia]

    Special engine value: rankings = [qs, shanghai, the]

    Args:
        engines (list[str]): The selected engines used for crawling
        commit (bool): Whether or not commit the ranking table to DB
        offline (bool): Only use CSV files (no web crawling)
    """
    all_not_matched = []
    all_fuzzy_matched = []
    # (name -> ror_id) and (link -> ror_id) of past confident matches, so a
    # renamed-but-same-URL entry resolves without re-hitting the ROR API.
    cache_path = crwc.DATA_DIR / "affiliation_cache.json"
    cache: dict[str, dict[str, str]] = (
        json.loads(cache_path.read_text(encoding="utf-8"))
        if cache_path.exists()
        else {"names": {}, "links": {}}
    )
    for engine in engines:
        typer.secho(f"Processing '{engine}' urls.", fg=typer.colors.CYAN)
        config, crawler = engine_select(engine)
        if engine == "wikipedia":
            # The WikipediaCrawler class works a little different.
            urls = get_wikipedia_urls() or config.URLS
            for url in urls:
                w = crawler(url["ror_id"], url["wikipedia_url"])
                w.crawl()
            continue

        stmt = (
            select(d.Institution.ror_id)
            .join(d.Institution.types)
            .where(d.Type.type == e.InstTypeEnum.Education)
            .distinct()
        )
        with d.SessionLocal() as db:
            institution_repo = r.InstitutionRepo(db)
            # ROR ids typed "Education": used to break fuzzy-match ties toward
            # the canonical university (not a hospital / facility / sub-unit).
            education_rors: set[str] = set(db.scalars(stmt).all())
            # Group soup by country for better performance.
            soup: dict[str, dict[str, str]] = {}
            for inst in institution_repo.get_db_institutions(limit=0):
                if not inst.country or inst.soup is None:
                    continue
                soup.setdefault(inst.country.country, {})[inst.soup] = inst.ror_id

            for page in config.URLS:
                if not page.get("crawl"):
                    continue

                crawl_mode = "online"
                ranking_info = {
                    "ranking_system": page["ranking_system"],
                    "ranking_type": page["ranking_type"],
                    "year": page["year"],
                    "field": page["field"],
                    "subject": page["subject"],
                }

                p = crawler(url=page["url"], **ranking_info)
                if offline and not p.file_path.exists():
                    continue
                if p.file_path.exists():
                    p = c.OfflineCrawler(url=page["url"], **ranking_info)
                    crawl_mode = "offline"

                typer.secho(
                    "Processing: "
                    + " ".join(map(str, ranking_info.values()))
                    + f" [{crawl_mode}]",
                    fg=typer.colors.CYAN,
                )

                matched, not_matched, fuzzy_matched = p.crawl_and_process(
                    institution_repo=institution_repo,
                    soup=soup,
                    education_rors=education_rors,
                    cache=cache,
                    use_api=not offline,
                )
                if commit:
                    db.add_all(matched)
                    db.commit()
                all_fuzzy_matched.extend(fuzzy_matched)
                all_not_matched.extend(not_matched)

    cache_path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if all_fuzzy_matched:
        csv_export(crwc.DATA_DIR / "fuzz.csv", all_fuzzy_matched)
        typer.echo("Saved the list of fuzzy-matched institutions.")
    if all_not_matched:
        csv_export(crwc.DATA_DIR / "not_mached.csv", all_not_matched)
        typer.echo("Saved the list of not matched institutions.")

    typer.secho("All done!", fg=typer.colors.GREEN)
