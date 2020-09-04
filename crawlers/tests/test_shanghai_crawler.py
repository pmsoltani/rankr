import pytest

from crawlers.shanghai_crawler import shac, ShanghaiCrawler


class TestShanghaiCrawlerCandidates(object):
    @pytest.fixture(autouse=True)
    def setup_method(self):
        ranking_info1: dict = [
            r
            for r in shac.URLS
            if r["year"] == 2018 and "Candidates" in r["url"]
        ][0]
        ranking_info1 = {k: v for k, v in ranking_info1.items() if k != "crawl"}
        self.shanghai1 = ShanghaiCrawler(**ranking_info1)

        ranking_info2: dict = [
            r
            for r in shac.URLS
            if r["year"] == 2019 and r["ranking_type"] == "university ranking"
        ][0]
        ranking_info2 = {k: v for k, v in ranking_info2.items() if k != "crawl"}
        self.shanghai2 = ShanghaiCrawler(**ranking_info2)

    def test_shanghai_crawler_candidates(self):
        with pytest.raises(AttributeError):
            assert self.shanghai1.page

        self.shanghai1._get_page()

        with pytest.raises(AttributeError):
            assert self.shanghai1.processed_data

        self.shanghai1._get_tbl()
        assert (
            self.shanghai1.processed_data[3]["Institution"]
            == "Bangor University"
        )
        assert self.shanghai1.processed_data[3]["Alumni"] == "11.4"

    def test_shanghai_crawler(self):
        with pytest.raises(AttributeError):
            assert self.shanghai2.page

        self.shanghai2._get_page()

        with pytest.raises(AttributeError):
            assert self.shanghai2.processed_data

        self.shanghai2._get_tbl()
        assert (
            self.shanghai2.processed_data[37]["Institution"]
            == "Karolinska Institute"
        )
        assert self.shanghai2.processed_data[37]["Total Score"] == "35.8"
