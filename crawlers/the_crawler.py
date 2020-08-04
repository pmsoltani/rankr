import json
import re
from typing import List

import requests
from furl import furl

from config import THEConfig
from crawlers import CrawlerMixin
from utils import text_process


class THECrawler(CrawlerMixin, THEConfig):
    def __init__(self, url: str, **kwargs):
        self.urls = [url]
        super().__init__(**kwargs)

    def _get_page(self):
        page = requests.get(self.urls[0], headers=self.headers)
        json_url = re.findall(r"(https.*?\.json)", page.text)[0]

        self.json_url = json_url.replace("\\", "")
        return self.json_url

    def _get_tbl(self):
        page = requests.get(self.json_url, headers=self.headers)
        raw_data = json.loads(page.text)

        # processing raw_data
        processed_data: List[dict] = []
        for row in raw_data["data"]:
            values = {}
            for col in row:
                if col not in THEConfig.FIELDS:
                    continue

                value = row[col] if row[col] else ""
                if THEConfig.FIELDS[col] == "Country":
                    value = THECrawler.country_name_mapper(text_process(value))
                if THEConfig.FIELDS[col] == "URL":
                    value = furl(THEConfig.BASE_URL).join(value)

                values[THEConfig.FIELDS[col]] = value

            processed_data.append({**values, **self.ranking_info})

        self.processed_data = processed_data
        return self.processed_data
