import re
import time
from contextlib import closing
from typing import Dict, List

import requests
from bs4 import BeautifulSoup, Tag
from furl import furl
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from tqdm import trange

from config import enums as e, shac
from rankr import schemas as s
from rankr.crawlers.crawler_mixin import CrawlerMixin
from rankr.schemas.validators import text_process


class ShanghaiCrawler(CrawlerMixin):
    def __init__(
        self, url: str, driver_path: str = "chromedriver", **kwargs
    ) -> None:
        self.url = url
        self.download_dir = shac.DOWNLOAD_DIR

        self.driver_path = driver_path
        self.metrics = ["alumni", "award", "hici", "n&s", "pub", "pcp"]
        if kwargs["ranking_type"] == e.RankingTypeEnum["subject ranking"].name:
            self.metrics = ["q1", "cnci", "ic", "top", "award"]

        super().__init__(**kwargs)

    def _get_driver(self):
        options = Options()
        options.add_argument("--disable-notifications")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(
            executable_path=self.driver_path, options=options
        )

    def _get_page(self) -> int:
        page = requests.get(self.url, headers=shac.HEADERS)
        page.raise_for_status()

        soup = BeautifulSoup(page.content, "html.parser")
        li_tags: List[Tag] = soup.select("li.ant-pagination-item")
        self._last_page_number = int(li_tags[-1].text)
        return self._last_page_number

    def _get_tbl(self) -> List[Dict[str, str]]:
        """Finds the ranking table within the page & extracts the data.

        Returns:
            List[Dict[str, str]]: Table data as a list of dictionaries
        """
        self.processed_data: List[Dict[str, str]] = []
        with closing(self._get_driver()) as d:
            d.get(self.url)
            for page in trange(self._last_page_number, desc="Crawling pages"):
                li_tags: List[WebElement] = d.find_elements_by_tag_name("li")
                values = {}
                for metric in self.metrics:
                    scores_button = d.find_elements_by_class_name("head-bg")[-1]
                    scores_button.click()

                    score_tag = [
                        t for t in li_tags if t.text.lower() == metric
                    ][0]
                    score_tag.click()

                    soup = BeautifulSoup(d.page_source, "html.parser")
                    values = {
                        k: {**values.get(k, {}), **v}
                        for k, v in self._get_metric(soup, metric).items()
                    }

                self.processed_data.extend(
                    [{**v, **self.ranking_info} for v in values.values()]
                )

                # click next page
                next_page_button = d.find_elements_by_class_name(
                    "ant-pagination-item-link",
                )[-1]
                next_page_button.click()

                # scroll to top
                js = "var action=document.documentElement.scrollTop=0"
                d.execute_script(js)
                time.sleep(1)
        return self.processed_data

    def _get_col_names(self, soup: BeautifulSoup):
        col_names = []
        for col in soup.select("table thead th"):
            col = text_process(col.text)
            col = col.lower() if col else ""
            if "institution" in col:
                col_names.extend(["url", "institution", "country"])

            if col in shac.FIELDS:
                col_names.append(shac.FIELDS[col])
        return col_names

    def _get_metric(self, soup: BeautifulSoup, metric: str):
        pattern = r"^.*?png100\/(.*?).png.*?$"
        page_values = []

        col_names = [*self._get_col_names(soup), metric]

        for row in soup.select("table tbody tr"):
            row_values = []
            for index, col in enumerate(row.select("td")):
                if index == 1:
                    url = None
                    a_tag = col.find("a")
                    if isinstance(a_tag, Tag):
                        url = furl(shac.BASE_URL).join(a_tag["href"]).url
                    row_values.append(url)
                    span_tag = col.find("span")
                    assert isinstance(span_tag, Tag)
                    row_values.append(span_tag.text.strip())
                    continue
                if index == 2:
                    flag_tag = col.select_one(".region-img")
                    assert isinstance(flag_tag, Tag)
                    flag_url = flag_tag["style"]
                    if isinstance(flag_url, list):
                        flag_url = flag_url[0]
                    country = s.CountryCreate(
                        country="",
                        country_code=re.findall(pattern, flag_url)[0],
                    )
                    row_values.append(country.country)
                    continue

                row_values.append(col.text.strip())

            page_values.append(dict(zip(col_names, row_values)))
        return {r["institution"]: r for r in page_values}
