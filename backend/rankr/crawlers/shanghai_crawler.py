from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from furl import furl

from config import enums as e, shac
from rankr import schemas as s
from rankr.crawlers.crawler_mixin import CrawlerMixin
from utils import text_process

from devtools import debug


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
        page.raise_for_status()

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
            tbl_headers = [h for h in tbl_headers if h != "url"]

        for row in tbl.find_all("tr"):
            values = []
            for val in row.find_all("td"):
                if val.find("img"):
                    # Get country name from the country flag images.
                    country = s.CountryCreate(
                        country=Path(val.find("img")["src"]).stem
                    )
                    values.append(country.country)
                    continue
                if val.find("a") and val.text:
                    url = furl(shac.BASE_URL) / val.find("a")["href"]
                    values.append(url.url)
                values.append(val.text)

            if values:
                values = dict(zip(tbl_headers, values))
                values["url"] = values.get("url") or None
                values["total score"] = values.get("total score") or None
                values = {
                    k: self._value_to_schema(key=k, value=v)
                    for k, v in values.items()
                }
                debug(values)
                raise ValueError
                # Some of the Shanghai ranking tables may not have the
                # 'url' or the 'Total Score' fields. If so, we add them:

                self.processed_data.append({**values, **self.ranking_info})
                debug(self.processed_data)
                raise ValueError

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
                new_headers.extend(["url", "institution", "country"])

            if h in shac.FIELDS:
                new_headers.append(shac.FIELDS[h])

            if h.startswith("score on"):
                tmp = h.replace("score on", "").strip().split(" ")
                tmp = [shac.FIELDS[t] for t in tmp if t.strip()]
                new_headers.extend(tmp)

        return new_headers

    def _value_to_schema(self, key: str, value: str):
        key = key.lower()
        print(key, value, self.ranking_info)
        if key == "url":
            return s.LinkCreate(link=value, type=e.LinkTypeEnum.shanghai)
        if key == "country":
            return s.CountryCreate(country=value)
        if key == "institution":
            return value

        metric = shac.RANKINGS["metrics"]["shanghai"][key]["name"]
        value_type = shac.RANKINGS["metrics"]["shanghai"][key]["type"]
        return s.RankingCreate(
            **self.ranking_info,
            metric=metric,
            raw_value=value,
            value_type=value_type,
        )
