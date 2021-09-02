import errno
import os

from config import crwc
from rankr.crawlers.crawler_mixin import CrawlerMixin
from utils import get_row


class OfflineCrawler(CrawlerMixin):
    def __init__(self, url: str, **kwargs) -> None:
        self.url = url
        self.download_dir = crwc.DATA_DIR / kwargs["ranking_system"]
        super().__init__(**kwargs)

    def _get_page(self):
        pass

    def _get_tbl(self):
        if not self.file_path.exists():
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.file_path.name
            )
        self.processed_data = list(get_row(self.file_path))
        return self.processed_data
