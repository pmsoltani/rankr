import pytest

from crawlers.wikipedia_crawler import wikic, WikipediaCrawler


class TestWikipediaCrawler(object):
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.url = "https://en.wikipedia.org/wiki/Stanford_University"
        self.file_name = "test_logo"
        self.file_ext = ".svg"
        self.w = WikipediaCrawler(grid_id=self.file_name, url=self.url)
        self.w.file_path = wikic.DATA_DIR / self.file_name

    def test_qs_crawler(self):
        try:
            assert not self.w.file_path.with_suffix(self.file_ext).exists()
            self.w.crawl()
            assert self.w.file_path.with_suffix(self.file_ext).exists()
        finally:
            try:
                self.w.file_path.with_suffix(self.file_ext).unlink()
            except FileNotFoundError:
                pass
