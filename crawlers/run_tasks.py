from config import BaseConfig, QSConfig, ShanghaiConfig, THEConfig
from crawlers import QSCrawler, ShanghaiCrawler, THECrawler


def engine_select(engine: str):
    if engine == "QS":
        return (QSConfig, QSCrawler)
    if engine == "Shanghai":
        return (ShanghaiConfig, ShanghaiCrawler)
    if engine == "THE":
        return (THEConfig, THECrawler)


if __name__ == "__main__":
    for engine in BaseConfig.CRAWLER_ENGINE:
        config, crawler = engine_select(engine)
        for page in config.URLS:
            if not page.get("crawl"):
                continue
            p = crawler(
                page["url"], page["year"], page["field"], page["subject"]
            )
            p.crawl()
