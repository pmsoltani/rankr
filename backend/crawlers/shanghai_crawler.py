from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from furl import furl

from config import shac
from crawlers.crawler_mixin import CrawlerMixin
from utils import text_process


class ShanghaiCrawler(CrawlerMixin):
    def __init__(self, url: str, **kwargs) -> None:
        self.url = url
        self.download_dir = shac.DOWNLOAD_DIR
        self.header_group_keyword: str = "institution"

        super().__init__(**kwargs)

    def _get_page(self) -> BeautifulSoup:
        """Requests a page for data extraction.

        Raises:
            ConnectionError: If the request is not successful

        Returns:
            BeautifulSoup: The downloaded page
        """
        page = requests.get(self.url, headers=shac.HEADERS)
        if page.status_code != 200:
            raise ConnectionError(f"Error getting page: {self.url}")

        self.page = BeautifulSoup(page.content, "html.parser")
        return self.page

    def _get_tbl(self) -> List[Dict[str, str]]:
        """Finds the ranking table within the page & extracts the data.

        Returns:
            List[Dict[str, str]]: Table data as a list of dictionaries
        """
        self.processed_data: List[Dict[str, str]] = []

        tbl = self.page.find("table", attrs={"id": "UniversityRanking"})

        # Get table headers.
        tbl_headers = self._clean_headers([h.text for h in tbl.find_all("th")])
        if not tbl.find_all("tr")[1].find("a"):
            tbl_headers = [h for h in tbl_headers if h != "URL"]

        for row in tbl.find_all("tr"):
            values = []
            for val in row.find_all("td"):
                if val.find("img"):
                    # Get country name from the country flag images.
                    country = Path(val.find("img")["src"]).stem
                    country = shac.country_name_mapper(text_process(country))
                    values.append(country)
                    continue
                if val.find("a") and val.text:
                    url = furl(shac.BASE_URL) / val.find("a")["href"]
                    values.append(url.url)
                values.append(val.text)

            if values:
                values = dict(zip(tbl_headers, [v.strip() for v in values]))
                # Some of the Shanghai ranking tables may not have the
                # 'URL' or the 'Total Score' fields. If so, we add them:
                values["URL"] = values.get("URL") or None
                values["Total Score"] = values.get("Total Score") or None
                self.processed_data.append({**values, **self.ranking_info})

        if not tbl_headers or not self.processed_data:
            raise ConnectionError("Error getting page!")
        return self.processed_data

    def _clean_headers(self, headers: List[str]) -> List[str]:
        """Cleans a list of headers

        Args:
            headers (List[str]): Raw header names

        Returns:
            List[str]: Cleaned column names
        """
        new_headers: List[str] = []

        for h in headers:
            h = text_process(h).lower()
            if self.header_group_keyword in h:
                new_headers.extend(["URL", "Institution", "Country"])

            if h in shac.FIELDS:
                new_headers.append(shac.FIELDS[h])

            if h.startswith("score on"):
                tmp = h.replace("score on", "").strip().split(" ")
                tmp = [shac.FIELDS[t] for t in tmp if t.strip()]
                new_headers.extend(tmp)

        return new_headers
