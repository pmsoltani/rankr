from typing import List, Tuple

from furl import furl

from config import QSConfig
from crawlers import CrawlerMixin
from utils import text_process


class QSCrawler(CrawlerMixin, QSConfig):
    def __init__(
        self,
        url: str,
        use_js: bool = True,
        merge_on_cols: List[str] = ["Rank", "Institution", "URL"],
        **kwargs,
    ):
        self.urls = [url]
        self.use_js = use_js
        self.merge_on_cols = merge_on_cols
        self.header_group_keyword = "university"

        super().__init__(**kwargs)

    def _get_tbl(self) -> Tuple[List[List[str]], List[List[List[str]]]]:
        """Finds the ranking table within the page and extracts its data

        Returns:
            Tuple[List[str], List[List[str]]]: Table headers and content
        """
        self.tbl_headers: List[List[str]] = []
        self.tbl_contents: List[List[List[str]]] = []
        for page in self.pages:
            tbl = page.find("table", attrs={"id": "qs-rankings-indicators"})

            tbl_headers = [
                h.text for h in tbl.find("thead").find("tr").find_all("th")
            ]
            tbl_headers = self._clean_headers(tbl_headers)
            self.tbl_headers.append(tbl_headers)

            tbl_contents: List[List[str]] = []
            for row in tbl.find("tbody").find_all("tr"):
                values = []
                for val in row.find_all("td"):
                    if "uni" in val.get("class", []):
                        url_elem = val.find("a", attrs={"class": "title"})
                        if not url_elem:
                            url_elem = val.find("a")
                        url = furl(url_elem["href"]).copy().set(fragment="")
                        url = furl(QSConfig.BASE_URL).join(url)
                        print(url)

                        values.append(url.url)
                        values.append(url_elem.text)
                        continue
                    if "country" in val.get("class", []):
                        country = QSCrawler.country_name_mapper(
                            text_process(val.text)
                        )
                        values.append(country)
                        continue
                    values.append(val.text)

                if values:
                    tbl_contents.append([v.strip() for v in values])
            self.tbl_contents.append(tbl_contents)

        if not self.tbl_headers or not self.tbl_contents:
            raise ConnectionError(f"Error getting page: {self.url}")
        return (self.tbl_headers, self.tbl_contents)

    def _clean_headers(self, headers: List[str]) -> list:
        """Cleans a list of headers

        Returns:
            list: Cleaned column names
        """
        new_headers = []

        for h in headers:
            h = text_process(h)
            if self.header_group_keyword in h.lower():
                new_headers.extend(["URL", "Institution", "Country"])

            if QSCrawler.FIELDS.get(h):
                new_headers.append(QSCrawler.FIELDS.get(h))

        return new_headers


if __name__ == "__main__":
    import io
    from bs4 import BeautifulSoup

    files = [QSConfig.MAIN_DIR / file for file in ["qs2.html"]]
    pages = []
    for file in files:
        pages.append(
            BeautifulSoup(io.open(file, "r", encoding="utf-8"), "html.parser")
        )
    q = QSCrawler(
        url="hi",
        year=2020,
        ranking_system="qs",
        ranking_type="university ranking",
        field="all",
        subject="all",
    )
    q.pages = pages
    q._get_tbl()
    q._csv_export()
