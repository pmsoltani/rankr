import io
import csv
import time
from pathlib import Path
from typing import List, Tuple

from requests_html import HTMLSession
from bs4 import BeautifulSoup
from furl import furl

from config import THEConfig
from utils import text_process


class THECrawler(THEConfig):
    def __init__(
        self,
        url: str,
        year: int,
        url_paths: Tuple[str] = ("stats", "scores"),
        use_js: bool = True,
        field: str = "All",
        subject: str = "All",
        wait: int = 10,
        tries: int = 5,
    ):
        self.url = furl(url)
        self.url_paths = url_paths
        self.use_js = use_js
        self.year = year
        self.field = field
        self.subject = subject

        self.wait = wait
        self.tries = tries

        self.file_name = f"THE_{self.year}_{self.field}_{self.subject}.csv"
        self.file_path = Path(THECrawler.DOWNLOAD_DIR) / self.file_name
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def crawl(self):
        for i in range(self.tries):
            try:
                self.ـget_page()
                self.ـget_tbl()
                self._tbl_merger(
                    on_cols=["Rank", "University", "Country", "URL"]
                )
                self.ـcsv_export()
            except ConnectionError as exc:
                print(exc, type(exc))
                print(f"Waiting for {self.wait} seconds.")
                time.sleep(self.wait)
                continue

            break

    def ـget_page(self) -> BeautifulSoup:
        """Requests a page for data extraction

        Raises:
            ConnectionError: If the request is not successful

        Returns:
            BeautifulSoup: Soup
        """
        session = HTMLSession()
        urls = [self.url + "/stats", self.url + "/scores"]
        self.pages = []
        try:
            for url in urls:
                page = session.get(url, headers=THECrawler.headers)
                if page.status_code != 200:
                    raise ConnectionError(f"Error getting page: {url}")
                page.html.render()
                self.pages.append(BeautifulSoup(page.html.html, "html.parser"))

                print(f"Downloaded page: {url}")
            return self.pages
        except Exception:
            pass
        finally:
            session.close()

    def ـget_tbl(self) -> Tuple[List[List[str]], List[List[List[str]]]]:
        """Finds the ranking table within the page and extracts its data

        Returns:
            Tuple[List[str], List[List[str]]]: Table headers and content
        """
        self.tbl_headers: List[List[str]] = []
        self.tbl_contents: List[List[List[str]]] = []
        for page in self.pages:
            tbl = page.find("table", attrs={"id": "datatable-1"})

            tbl_headers = [h.text for h in tbl.find("thead").find_all("th")]
            tbl_headers = self.ـclean_headers(tbl_headers)
            self.tbl_headers.append(tbl_headers)

            tbl_contents: List[List[str]] = []
            for row in tbl.find("tbody").find_all("tr"):
                values = []
                for val in row.find_all("td"):
                    if val["class"] == ["name", "namesearch"]:
                        url_elem = val.find(
                            "a", attrs={"class": "ranking-institution-title"}
                        )
                        country_elem = val.find(
                            "div", attrs={"class", "location"}
                        )
                        values.append(THEConfig.BASE_URL + url_elem["href"])
                        values.append(url_elem.text)
                        values.append(text_process(country_elem.text))
                        continue
                    values.append(val.text)

                if values:
                    tbl_contents.append(values)
            self.tbl_contents.append(tbl_contents)

        if not self.tbl_headers or not self.tbl_contents:
            raise ConnectionError(f"Error getting page: {self.url}")
        return (self.tbl_headers, self.tbl_contents)

    def ـcsv_export(self):
        """Exports a table to a .csv file."""
        with io.open(
            self.file_path, "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            writer.writerow(self.tbl_headers[0] + ["Year", "Field", "Subject"])
            writer.writerows(
                row + [self.year, self.field, self.subject]
                for row in (self.tbl_contents[0])
            )
            print(f"Saved file: {self.file_path}")

    def ـclean_headers(self, headers: List[str]) -> list:
        """Cleans a list of headers

        Returns:
            list: Cleaned column names
        """
        new_headers = []

        for h in headers:
            h = text_process(h)
            if h.startswith("NameCountry/Region"):
                new_headers.extend(["URL", "University", "Country"])

            if THECrawler.FIELDS.get(h):
                new_headers.append(THECrawler.FIELDS.get(h))

        return new_headers

    def _tbl_merger(self, on_cols: List[str]) -> List[List[str]]:
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

        return (self.tbl_headers[0], self.tbl_contents[0])
