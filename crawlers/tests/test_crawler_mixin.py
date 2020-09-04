import pytest

from crawlers.qs_crawler import qsc, QSCrawler


class TestCrawlerMixin(object):
    @pytest.fixture(autouse=True)
    def setup_method(self):
        ranking_info: dict = qsc.URLS[0]
        ranking_info = {k: v for k, v in ranking_info.items() if k != "crawl"}
        self.qs = QSCrawler(**ranking_info)
        self.qs.file_name = "test_ranking_table.csv"
        self.qs.file_path = qsc.DATA_DIR / self.qs.file_name

    def test_crawler_mixin(self):
        try:
            assert not self.qs.file_path.exists()
            self.qs.crawl()
            assert self.qs.file_path.exists()
        finally:  # cleaning up the mess
            try:
                self.qs.file_path.unlink()
            except FileNotFoundError:
                pass
