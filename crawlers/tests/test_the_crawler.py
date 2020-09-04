from furl import furl
import pytest

from crawlers.the_crawler import thec, THECrawler


class TestTHECrawler(object):
    @pytest.fixture(autouse=True)
    def setup_method(self):
        ranking_info: dict = [
            r
            for r in thec.URLS
            if r["year"] == 2020 and r["ranking_type"] == "university ranking"
        ][0]
        ranking_info = {k: v for k, v in ranking_info.items() if k != "crawl"}
        self.node_number = 121321
        self.the = THECrawler(**ranking_info)

    def test_the_crawler(self):
        with pytest.raises(AttributeError):
            assert self.the.json_url

        json_url = (
            furl(thec.BASE_URL)
            / "sites/default/files/the_data_rankings/"
            / (
                "world_university_rankings_2020_0__"
                + "24cc3874b05eea134ee2716dbf93f11a.json"
            )
        )
        self.the._get_page()
        assert self.the.json_url == json_url.url

        with pytest.raises(AttributeError):
            assert self.the.processed_data

        self.the._get_tbl()
        assert self.the.processed_data[23]["Institution"] == "Peking University"
        assert self.the.processed_data[23]["Overall"] == "82.3"
