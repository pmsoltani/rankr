import io
import csv
import time
from pathlib import Path
from typing import List, Tuple

from requests_html import HTMLSession
from bs4 import BeautifulSoup

from config import THEConfig


def vacuum(string: str) -> str:
    """Cleans the input text for further processing

    Args:
        string (str): Input text

    Returns:
        str: Clean text
    """
    string = string.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return " ".join([word for word in string.split(" ") if word])


class THECrawler(THEConfig):
    def __init__(
        self,
        url: str,
        year: int,
        field: str = "All",
        subject: str = "All",
        wait: int = 10,
        tries: int = 5,
    ):
        self.url = url
        self.year = year
        self.field = field
        self.subject = subject

        self.wait = wait
        self.tries = tries

        self.file_name = f"THE_{self.year}_{self.field}_{self.subject}.csv"
        self.file_path = Path(THECrawler.MAIN_DIR) / self.file_name
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def crawl(self):
        for i in range(self.tries):
            try:
                self.ـget_page()
                self.ـget_tbl()
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
        page = session.get(self.url, headers=THECrawler.headers)
        if page.status_code != 200:
            raise ConnectionError(f"Error getting page: {self.url}")
        page.html.render()
        self.page = BeautifulSoup(page.html.html, "html.parser")
        print(f"Downloaded page: {self.url}")
        return self.page

    def ـget_tbl(self) -> Tuple[List[str], List[List[str]]]:
        """Finds the ranking table within the page and extracts its data

        Returns:
            Tuple[List[str], List[List[str]]]: Table headers and content
        """
        tbl = self.page.find("table", attrs={"id": "datatable-1"})

        self.tbl_headers: List[str] = [
            h.text for h in tbl.find("thead").find_all("th")
        ]
        self.ـclean_headers()

        self.tbl_contents: List[List[str]] = []
        for row in tbl.find("tbody").find_all("tr"):
            values = []
            for val in row.find_all("td"):
                if val["class"] == ["name", "namesearch"]:
                    url_elem = val.find(
                        "a", attrs={"class": "ranking-institution-title"}
                    )
                    country_elem = val.find("div", attrs={"class", "location"})
                    values.append(THEConfig.BASE_URL + url_elem["href"])
                    values.append(url_elem.text)
                    values.append(country_elem.text)
                    continue
                values.append(val.text)

            if values:
                values.extend([self.year, self.field, self.subject])
                self.tbl_contents.append(values)

        return (self.tbl_headers, self.tbl_contents)

    def ـcsv_export(self):
        """Exports a table to a .csv file."""
        with io.open(
            self.file_path, "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            writer.writerow(self.tbl_headers)
            writer.writerows(row for row in self.tbl_contents if row)
            print(f"Saved file: {self.file_path}")

    def ـclean_headers(self) -> list:
        """Cleans a list of headers

        Returns:
            list: Cleaned column names
        """
        new_headers = []

        for h in self.tbl_headers:
            h = vacuum(h)
            if h.startswith("NameCountry/Region"):
                new_headers.extend(["URL", "University", "Country"])

            if THECrawler.FIELDS.get(h):
                new_headers.append(THECrawler.FIELDS.get(h))

        new_headers.extend(["Year", "Field", "Subject"])

        self.tbl_headers = new_headers
        return self.tbl_headers


if __name__ == "__main__":
    for page in THEConfig.URLS:
        if not page.get("crawl"):
            continue
        p = THECrawler(
            page["url"], page["year"], page["field"], page["subject"]
        )
        p.crawl()
