from config import CrawlerConfig, QSConfig, ShanghaiConfig, THEConfig
from crawlers import QSCrawler, ShanghaiCrawler, THECrawler


def engine_select(engine: str):
    if engine == "qs":
        return (QSConfig, QSCrawler)
    if engine == "shanghai":
        return (ShanghaiConfig, ShanghaiCrawler)
    if engine == "the":
        return (THEConfig, THECrawler)


if __name__ == "__main__":
    for engine in CrawlerConfig.CRAWLER_ENGINE:
        config, crawler = engine_select(engine)
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
