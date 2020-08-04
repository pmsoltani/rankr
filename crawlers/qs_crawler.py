import json
import re
from typing import List

import requests
from bs4 import BeautifulSoup
from furl import furl

from config import QSConfig
from crawlers import CrawlerMixin
from utils import text_process


class QSCrawler(CrawlerMixin, QSConfig):
    def __init__(self, url: str, **kwargs):
        self.urls = [url]
        super().__init__(**kwargs)

    def _get_page(self):
        page = requests.get(self.urls[0], headers=self.headers)
        link = page.headers["link"]
        node_number = re.findall(r".*?node/(.*?)>.*?", link)[0]

        json_url = (
            furl(QSConfig.BASE_URL)
            / "sites/default/files/qs-rankings-data/"
            / f"{node_number}_indicators.txt"
        )
        self.json_url = json_url
        return self.json_url

    def _get_tbl(self):
        page = requests.get(self.json_url, headers=self.headers)
        raw_data = json.loads(page.text)

        # getting columns:
        columns = {}
        for col in raw_data["columns"]:
            col_disp = BeautifulSoup(col["title"], "html.parser").text
            col_name = QSConfig.FIELDS.get(col_disp.lower(), None)
            if not col_name:
                continue
            columns[col["data"]] = col_name

        # processing raw_data
        processed_data: List[dict] = []
        for row in raw_data["data"]:
            values = {}
            for col in row:
                if col not in columns:
                    continue

                if not row[col]:
                    # None values make BeautifulSoup raise exception
                    row[col] = ""
                value = BeautifulSoup(row[col], "html.parser")
                if columns[col] == "Country":
                    country = QSCrawler.country_name_mapper(
                        text_process(value.text)
                    )
                    values[columns[col]] = country
                    continue
                if columns[col] == "Institution":
                    values["URL"] = furl(QSConfig.BASE_URL).join(
                        value.find("a")["href"]
                    )
                    values[columns[col]] = value.text
                    continue

                values[columns[col]] = value.text

            processed_data.append({**values, **self.ranking_info})

        self.processed_data = processed_data
        return self.processed_data
