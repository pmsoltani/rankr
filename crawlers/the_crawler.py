from pathlib import Path
from typing import List, Tuple

from furl import furl

from config import THEConfig
from crawlers import CrawlerMixin
from utils import text_process


class THECrawler(CrawlerMixin, THEConfig):
    def __init__(
        self,
        url: str,
        year: int,
        url_paths: List[str] = ["stats", "scores"],
        use_js: bool = True,
        ranking_system: str = "the",
        ranking_type: str = "university ranking",
        field: str = "All",
        subject: str = "All",
        merge_on_cols: List[str] = ["Rank", "University", "Country", "URL"],
        wait: int = 10,
        tries: int = 5,
    ):
        fragments = [furl(url).fragment.add(p) for p in url_paths]
        self.urls = [furl(url).copy().set(fragment=str(f)) for f in fragments]
        self.use_js = use_js
        self.ranking_system = ranking_system
        self.ranking_type = ranking_type
        self.year = year
        self.field = field
        self.subject = subject

        self.wait = wait
        self.tries = tries

        self.file_name = f"THE_{self.year}_{self.field}_{self.subject}.csv"
        self.file_path = Path(THECrawler.DOWNLOAD_DIR) / self.file_name
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self.merge_on_cols = merge_on_cols

    def _get_tbl(self) -> Tuple[List[List[str]], List[List[List[str]]]]:
        """Finds the ranking table within the page and extracts its data

        Returns:
            Tuple[List[List[str]], List[List[List[str]]]]: Table headers
            and content
        """
        self.tbl_headers: List[List[str]] = []
        self.tbl_contents: List[List[List[str]]] = []
        for page in self.pages:
            tbl = page.find("table", attrs={"id": "datatable-1"})

            tbl_headers = [h.text for h in tbl.find("thead").find_all("th")]
            tbl_headers = self._clean_headers(tbl_headers)
            self.tbl_headers.append(tbl_headers)

            tbl_contents: List[List[str]] = []
            for row in tbl.find("tbody").find_all("tr"):
                values = []
                for val in row.find_all("td"):
                    if val["class"] == ["name", "namesearch"]:
                        url_elem = val.find(
                            "a", attrs={"class": "ranking-institution-title"}
                        )
                        url = furl(THEConfig.BASE_URL) / url_elem["href"]
                        country_elem = val.find(
                            "div", attrs={"class", "location"}
                        )
                        country = THECrawler.country_name_mapper(
                            text_process(country_elem.text)
                        )

                        values.append(url.url)
                        values.append(url_elem.text)
                        values.append(country)
                        continue
                    values.append(val.text)

                if values:
                    tbl_contents.append([v.strip() for v in values])
            self.tbl_contents.append(tbl_contents)

        if not self.tbl_headers or not self.tbl_contents:
            raise ConnectionError(f"Error getting page: {self.url}")
        return (self.tbl_headers, self.tbl_contents)

    def _clean_headers(self, headers: List[str]) -> List[str]:
        """Cleans a list of headers

        Args:
            headers (List[str]): The headers to be cleaned

        Returns:
            List[str]: Cleaned column names
        """
        new_headers = []

        for h in headers:
            h = text_process(h)
            if "country" in h.lower():
                new_headers.extend(["URL", "University", "Country"])

            if THECrawler.FIELDS.get(h):
                new_headers.append(THECrawler.FIELDS.get(h))

        return new_headers

    def _tbl_merger(
        self, on_cols: List[str]
    ) -> Tuple[List[str], List[List[str]]]:
        """Merges to tables using a specified list of columns.

        Args:
            on_cols (List[str]): The columns on which the function joins
            the two tables.

        Returns:
            Tuple[List[str], List[List[str]]]: Merged table headers and
            contents
        """
        if self.tbl_headers[0] == self.tbl_headers[1]:
            return (self.tbl_headers[0], self.tbl_contents[0])

        self.tbl_headers[0].extend(
            [c for c in self.tbl_headers[1] if c not in on_cols]
        )
        on_cols = [self.tbl_headers[1].index(c) for c in on_cols]

        for i, row in enumerate(self.tbl_contents[0]):
            row_match = True
            for c in on_cols:
                if row[c] != self.tbl_contents[1][i][c]:
                    row_match = False
                    break
            if not row_match:
                continue
            self.tbl_contents[0][i].extend(
                [
                    c
                    for j, c in enumerate(self.tbl_contents[1][i])
                    if j not in on_cols
                ]
            )

        self.tbl_headers = self.tbl_headers[0]
        self.tbl_contents = self.tbl_contents[0]

        return (self.tbl_headers, self.tbl_contents)
