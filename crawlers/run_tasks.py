from config import ShanghaiConfig
from crawlers.shanghai_crawler import ShanghaiCrawler


if __name__ == "__main__":
    for page in ShanghaiConfig.URLS:
        if not page.get('crawl'):
            continue
        p = ShanghaiCrawler(
            page["url"], page["year"], page["field"], page["subject"]
        )
        p.crawl()
