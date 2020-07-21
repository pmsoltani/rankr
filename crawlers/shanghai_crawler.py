import io
import csv
import time
from pathlib import Path
from typing import List, Tuple

import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup

from config import ShanghaiConfig


def vacuum(string: str) -> str:
    """Cleans the input text for further processing

    Args:
        string (str): Input text

    Returns:
        str: Clean text
    """
    string = string.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return " ".join([word for word in string.split(" ") if word])


def country_name_mapper(country: str) -> str:
    country_names = {
        "usa": "United States",
        "unitedstates": "United States",
        "uk": "United Kingdom",
        "unitedkingdom": "United Kingdom",
        "unitedarabemirates": "United Arab Emirates",
        "china-hongkong": "Hong Kong",
        "china-hk": "Hong Kong",
        "hongkong,china": "Hong Kong",
        "macau": "Macao",
        "china-macau": "Macao",
        "china-mc": "Macao",
        "china-taiwan": "Taiwan",
        "taiwan,china": "Taiwan",
        "china-tw": "Taiwan",
        "czech": "Czech Republic",
        "czechrepublic": "Czech Republic",
        "new zealand": "New Zealand",
        "puertorico": "Puerto Rico",
        "saudiarabia": "Saudi Arabia",
        "southafrica": "South Africa",
        "southkorea": "South Korea",
    }

    return country_names.get(country.lower(), country)


class ShanghaiCrawler(ShanghaiConfig):
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

        self.file_name = f"Shanghai_{self.year}_{self.field}_{self.subject}.csv"
        self.file_path = Path(ShanghaiCrawler.DOWNLOAD_DIR) / self.file_name
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
        page = requests.get(self.url, headers=ShanghaiCrawler.headers)
        if page.status_code != 200:
            raise ConnectionError(f"Error getting page: {self.url}")
        self.page = BeautifulSoup(page.content, "html.parser")
        print(f"Downloaded page: {self.url}")
        return self.page

    def ـget_tbl(self) -> Tuple[List[str], List[List[str]]]:
        """Finds the ranking table within the page and extracts its data

        Returns:
            Tuple[List[str], List[List[str]]]: Table headers and content
        """
        tbl = self.page.find("table", attrs={"id": "UniversityRanking"})

        self.tbl_headers: List[str] = [h.text for h in tbl.find_all("th")]
        self.ـclean_headers()

        self.tbl_contents: List[List[str]] = []
        for row in tbl.find_all("tr"):
            values = []
            for val in row.find_all("td"):
                if val.find("img"):
                    country = Path(val.find("img")["src"]).stem
                    values.append(country_name_mapper(country))
                    continue
                if val.find("a") and val.text:
                    values.append(
                        ShanghaiCrawler.BASE_URL + val.find("a")["href"]
                    )
                values.append(val.text)

            if values:
                self.tbl_contents.append(values)

        return (self.tbl_headers, self.tbl_contents)

    def ـcsv_export(self):
        """Exports a table to a .csv file."""
        with io.open(
            self.file_path, "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            writer.writerow(self.tbl_headers + ["Year", "Field", "Subject"])
            writer.writerows(
                row + [self.year, self.field, self.subject]
                for row in self.tbl_contents
                if row
            )
            print(f"Saved file: {self.file_path}")

    def ـclean_headers(self) -> list:
        """Cleans a list of headers

        Returns:
            list: Cleaned column names
        """
        new_headers = []
        if "url" not in [h.lower() for h in self.tbl_headers]:
            self.tbl_headers.insert(1, "URL")

        for h in self.tbl_headers:
            h = vacuum(h)
            if h.startswith("By location"):
                h = "By location"

            if ShanghaiCrawler.FIELDS.get(h):
                new_headers.append(ShanghaiCrawler.FIELDS.get(h))

            if h.startswith("Score on"):
                tmp = h.replace("Score on", "").strip().split(" ")
                tmp = [t for t in tmp if t.strip()]
                new_headers.extend(tmp)

        self.tbl_headers = new_headers
        return self.tbl_headers
