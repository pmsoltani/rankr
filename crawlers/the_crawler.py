import json
import re
from typing import Dict, List

import requests
from furl import furl

from config import THEConfig
from crawlers.crawler_mixin import CrawlerMixin
from utils import text_process


class THECrawler(CrawlerMixin, THEConfig):
    def __init__(self, url: str, **kwargs) -> None:
        self.url = url
        super().__init__(**kwargs)

    def _get_page(self) -> str:
        """Retrieves the URL of raw json data for the ranking table.

        When loading a ranking table in www.timeshighereducation.com,
        the browser sends a request to another address like:

        https://www.timeshighereducation.com/sites/default/files/
        the_data_rankings/world_..._0__bcc1cfb285432.json"

        Which is a json file, containing the ranking table data. So all
        we have to do is to find this address and retrieve the json.

        Returns:
            str: The url for the ranking table data
        """
        page = requests.get(self.url, headers=self.headers)
        json_url: str = re.findall(r"(https.*?\.json)", page.text)[0]

        self.json_url = json_url.replace("\\", "")
        return self.json_url

    def _get_tbl(self) -> List[Dict[str, str]]:
        """Processes raw ranking data into a list of dictionaries.

        Returns:
            List[Dict[str, str]]: Processed ranking data to be exported
        """
        page = requests.get(self.json_url, headers=self.headers)
        raw_data = json.loads(page.text)

        # processing raw_data
        processed_data: List[Dict[str, str]] = []
        for row in raw_data["data"]:
            values = {}
            for col in row:
                if col not in THEConfig.FIELDS:
                    continue

                value = row[col].strip() if row[col] else ""
                if THEConfig.FIELDS[col] == "Country":
                    value = THECrawler.country_name_mapper(text_process(value))
                if THEConfig.FIELDS[col] == "URL":
                    value = furl(THEConfig.BASE_URL).join(value)

                values[THEConfig.FIELDS[col]] = value

            processed_data.append({**values, **self.ranking_info})

        self.processed_data = processed_data
        return self.processed_data
