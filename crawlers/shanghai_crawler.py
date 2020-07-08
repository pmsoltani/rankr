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


def get_page(url: str) -> BeautifulSoup:
    """Requests a page for data extraction

    Args:
        url (str): URL of the page

    Raises:
        HTTPError: If the request is not successful

    Returns:
        BeautifulSoup: Soup
    """
    page = requests.get(url, headers=shc.headers)
    if page.status_code != 200:
        raise HTTPError(f"Error getting page: {url}")
    return BeautifulSoup(page.content, "html.parser")


def get_table(page) -> Tuple[List[str], List[List[str]]]:
    """Finds the ranking table within the page and extracts its data

    Args:
        page ([type]): The page to be processed
    Returns:
        Tuple[List[str], List[List[str]]]: Table headers and content
    """
    table = page.find("table", attrs={"id": "UniversityRanking"})
    headers = [header.text for header in table.find_all("th")]
    headers = clean_headers(headers)
    rows = []

    for row in table.find_all("tr"):
        values = []
        for val in row.find_all("td"):
            if val.find("img"):
                values.append(Path(val.find("img")["src"]).stem)
                continue
            if val.find("a") and val.text:
                values.append(shc.BASE_URL + val.find("a")["href"])
            values.append(val.text)

        rows.append(values)

    return (headers, rows)


def csv_export(table: Tuple[List[str], List], location: str):
    """Exports a table to a .csv file.

    Args:
        table (Tuple[List[str], List]): The table to be exported
        location (str): The location of the output file.
    """
    with io.open(location, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        writer.writerow(table[0])
        writer.writerows(row for row in table[1] if row)


p = get_page(shc.URL)
tbl = get_table(p)
csv_export(tbl, "test.csv")
