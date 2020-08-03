from pathlib import Path
from typing import List, Tuple

from furl import furl

from config import ShanghaiConfig
from crawlers import CrawlerMixin
from utils import text_process


class ShanghaiCrawler(CrawlerMixin, ShanghaiConfig):
    def __init__(self, url: str, **kwargs):
        self.urls = [url]
        self.use_js = False
        self.merge_on_cols = []
        self.header_group_keyword = "institution"

        super().__init__(**kwargs)

    def _get_tbl(self) -> Tuple[List[str], List[List[str]]]:
        """Finds the ranking table within the page and extracts its data

        Returns:
            Tuple[List[str], List[List[str]]]: Table headers and content
        """
        self.tbl_headers: List[List[str]] = []
        self.tbl_contents: List[List[List[str]]] = []
        for page in self.pages:
            tbl = page.find("table", attrs={"id": "UniversityRanking"})

            tbl_headers: List[str] = [h.text for h in tbl.find_all("th")]
            tbl_headers = self._clean_headers(tbl_headers)
            self.tbl_headers.append(tbl_headers)

            tbl_contents: List[List[str]] = []
            for row in tbl.find_all("tr"):
                values = []
                for val in row.find_all("td"):
                    if val.find("img"):
                        country = Path(val.find("img")["src"]).stem
                        country = ShanghaiCrawler.country_name_mapper(
                            text_process(country)
                        )
                        values.append(country)
                        continue
                    if val.find("a") and val.text:
                        url = (
                            furl(ShanghaiConfig.BASE_URL)
                            / val.find("a")["href"]
                        )
                        values.append(url.url)
                    values.append(val.text)

                if values:
                    tbl_contents.append([v.strip() for v in values])
            self.tbl_contents.append(tbl_contents)

        if not self.tbl_headers or not self.tbl_contents:
            raise ConnectionError("Error getting page!")
        return (self.tbl_headers, self.tbl_contents)

    def _clean_headers(self, headers: List[str]) -> List[str]:
        """Cleans a list of headers

        Returns:
            list: Cleaned column names
        """
        new_headers = []

        for h in headers:
            h = text_process(h)
            if self.header_group_keyword in h.lower():
                new_headers.extend(["URL", "Institution", "Country"])

            if ShanghaiCrawler.FIELDS.get(h):
                new_headers.append(ShanghaiCrawler.FIELDS.get(h))

            if h.startswith("Score on"):
                tmp = h.replace("Score on", "").strip().split(" ")
                tmp = [t for t in tmp if t.strip()]
                new_headers.extend(tmp)

        return new_headers
