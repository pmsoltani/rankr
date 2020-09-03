import json
import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from furl import furl

from config import qsc
from crawlers.crawler_mixin import CrawlerMixin
from utils import text_process


class QSCrawler(CrawlerMixin):
    def __init__(self, url: str, **kwargs) -> None:
        self.url = url
        self.download_dir = qsc.DOWNLOAD_DIR
        super().__init__(**kwargs)

    def _get_page(self) -> str:
        """Retrieves the URL of raw json data for the ranking table.

        QS ranking tables (in https://www.topuniversities.com/) each
        have a unique "node number". For example, QS World University
        Rankings has the following short-link in the page's metadata:

        https://www.topuniversities.com/node/946820

        When loading the page, the browser will send a request to
        another address with this node numer:

        https://www.topuniversities.com/
        sites/default/files/qs-rankings-data/946820_indicators.txt

        Which is a json file, containing the ranking table data. So all
        we have to do is to find this node number and retrieve the json.

        Returns:
            str: The url for the ranking table data
        """
        page = requests.get(self.url, headers=qsc.HEADERS)
        link = page.headers["link"]
        if "web.archive.org" in self.url:
            link = page.headers["X-Archive-Orig-Link"]
        node_number = re.findall(r".*?node/(.*?)>.*?", link)[0]

        json_url = (
            furl(qsc.BASE_URL)
            / "sites/default/files/qs-rankings-data/"
            / f"{node_number}_indicators.txt"
        )
        self.json_url = json_url.url
        return self.json_url

    def _get_tbl(self) -> List[Dict[str, str]]:
        """Processes raw ranking data into a list of dictionaries.

        Returns:
            List[Dict[str, str]]: Processed ranking data to be exported
        """
        page = requests.get(self.json_url, headers=qsc.HEADERS)
        raw_data = json.loads(page.text)

        # Column names are separated from actual data.
        columns = {}
        for col in raw_data["columns"]:
            col_disp = BeautifulSoup(col["title"], "html.parser").text
            col_name = qsc.FIELDS.get(col_disp.lower(), None)
            if not col_name:  # ignoring irrelevant data
                continue
            columns[col["data"]] = col_name

        # processing raw_data
        processed_data: List[Dict[str, str]] = []
        for row in raw_data["data"]:
            values = {}
            for col in row:
                if col not in columns:
                    continue

                if not row[col]:
                    # None values make BeautifulSoup raise exception.
                    row[col] = ""
                value = BeautifulSoup(row[col], "html.parser")
                if columns[col] == "Country":
                    country = qsc.country_name_mapper(text_process(value.text))
                    values[columns[col]] = country
                    continue
                if columns[col] == "Institution":
                    values["URL"] = furl(qsc.BASE_URL).join(
                        value.find("a")["href"]
                    )
                    values[columns[col]] = value.text.strip()
                    continue

                values[columns[col]] = value.text.strip()

            processed_data.append({**values, **self.ranking_info})

        self.processed_data = processed_data
        return self.processed_data
