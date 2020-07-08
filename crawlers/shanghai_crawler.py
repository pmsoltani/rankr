import io
import csv
from pathlib import Path
from typing import List, Tuple

import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup

from config import ShanghaiConfig as shc


def vacuum(string: str) -> str:
    """Cleans the input text for further processing

    Args:
        string (str): Input text

    Returns:
        str: Clean text
    """
    string = string.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return " ".join([word for word in string.split(" ") if word])


def clean_headers(headers: List[str]) -> list:
    """Cleans a list of headers

    Args:
        headers (List[str]): A list of column names to be cleaned

    Returns:
        list: Cleaned column names
    """
    new_headers = []
    if "url" not in [h.lower() for h in headers]:
        headers.insert(1, "URL")

    for h in headers:
        h = vacuum(h)
        if h.startswith("By location"):
            h = "By location"

        if shc.FIELDS.get(h):
            new_headers.append(shc.FIELDS.get(h))

        if h.startswith("Score on"):
            tmp = h.replace("Score on", "").strip().split(" ")
            tmp = [t for t in tmp if t.strip()]
            new_headers.extend(tmp)

    return new_headers


class ShanghaiCrawler(shc):
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

        self.file_name = f"ARWU_{self.year}_{self.field}_{self.subject}.csv"
        self.file_path = Path(shc.MAIN_DIR) / self.file_name
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def ـget_page(self) -> BeautifulSoup:
        """Requests a page for data extraction

        Raises:
            HTTPError: If the request is not successful

        Returns:
            BeautifulSoup: Soup
        """
        page = requests.get(self.url, headers=shc.headers)
        if page.status_code != 200:
            raise HTTPError(f"Error getting page: {self.url}")
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
                    values.append(country)
                    continue
                if val.find("a") and val.text:
                    values.append(shc.BASE_URL + val.find("a")["href"])
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


# p = get_page(shc.URL)
# tbl = get_table(p)
# csv_export(tbl, "test.csv")
