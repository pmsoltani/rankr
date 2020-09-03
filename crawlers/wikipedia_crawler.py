import shutil
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from furl import furl

from config import WikipediaConfig


class WikipediaCrawler(WikipediaConfig):
    def __init__(
        self, grid_id: str, url: str, wait: int = 10, tries: int = 5,
    ) -> None:
        self.grid_id = grid_id
        self.url = furl(url).set(scheme="https").url

        self.file_path = Path(self.DOWNLOAD_DIR) / self.grid_id
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self.wait = wait
        self.tries = tries

    def crawl(self) -> None:
        """Provides a high-level interface for the class."""
        for i in range(self.tries):
            try:
                self._get_page()
                self._get_logo()
                self._export_logo()
            except ConnectionError:
                print(f"Waiting for {self.wait} seconds.")
                time.sleep(self.wait)
                continue

            break

    def _get_page(self) -> Optional[BeautifulSoup]:
        """Retrieves the page containing the institution logo.

        Raises:
            ConnectionError: If the request is not successful

        Returns:
            BeautifulSoup: The downloaded logo page
        """
        wiki_page = requests.get(self.url, headers=self.headers)
        if wiki_page.status_code != 200:
            raise ConnectionError(f"Error getting page: {self.url}")

        wiki_page = BeautifulSoup(wiki_page.content, "html.parser")
        info_card = wiki_page.find(
            "table", attrs={"class": ["infobox", "vcard"]}
        )
        logo_page_elem = info_card.find_all("a", attrs={"class": "image"})
        if not logo_page_elem:
            return None

        logo_page_url = furl(self.BASE_URL) / logo_page_elem[0]["href"]
        logo_page = requests.get(logo_page_url, headers=self.headers)
        self.page = BeautifulSoup(logo_page.content, "html.parser")
        return self.page

    def _get_logo(self) -> Optional[requests.Response]:
        """[summary]

        Raises:
            ConnectionError: If the request is not successful

        Returns:
            Optional[requests.Response]: The stream of logo file
        """
        logo_elem = self.page.find("div", attrs={"id": "file"})
        if not logo_elem:
            return None

        logo_url = furl(logo_elem.find("a")["href"]).set(scheme="https").url
        file_ext = Path(logo_url).suffix.lower()
        if file_ext not in [".png", ".svg"]:
            return None

        logo = requests.get(logo_url, headers=self.headers, stream=True)
        if logo.status_code != 200:
            raise ConnectionError(f"Error getting page: {logo_url}")

        self.logo = logo
        self.file_ext = file_ext
        return self.logo

    def _export_logo(self) -> None:
        """Exports the logo to a file."""
        with open(self.file_path, "wb") as img_file:
            self.logo.raw.decode_content = True
            shutil.copyfileobj(self.logo.raw, img_file)
            self.file_path.rename(
                Path(self.DOWNLOAD_DIR) / (self.grid_id + self.file_ext)
            )
            print(f"Saved file: {self.file_path}{self.file_ext}")
