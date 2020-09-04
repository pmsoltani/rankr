from furl import furl
import pytest

from crawlers.qs_crawler import qsc, QSCrawler


class TestQSCrawler(object):
    @pytest.fixture(autouse=True)
    def setup_method(self):
        ranking_info: dict = [
            r
            for r in qsc.URLS
            if r["year"] == 2014 and r["ranking_type"] == "university ranking"
        ][0]
        ranking_info = {k: v for k, v in ranking_info.items() if k != "crawl"}
        self.node_number = 121321
        self.qs = QSCrawler(**ranking_info)

    def test_qs_crawler(self):
        with pytest.raises(AttributeError):
            assert self.qs.json_url

        json_url = (
            furl(qsc.BASE_URL)
            / "sites/default/files/qs-rankings-data/"
            / f"{self.node_number}_indicators.txt"
        )
        self.qs._get_page()
        assert self.qs.json_url == json_url.url

        with pytest.raises(AttributeError):
            assert self.qs.processed_data

        self.qs._get_tbl()
        assert self.qs.processed_data[7]["Institution"] == "Yale University"
        assert self.qs.processed_data[7]["Overall Score"] == "96.5"
