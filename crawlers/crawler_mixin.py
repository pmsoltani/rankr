import csv
import io
import time
from pathlib import Path
from typing import Union

from bs4 import BeautifulSoup
from requests_html import HTMLSession


class CrawlerMixin(object):
    def __init__(
        self,
        year: Union[str, int],
        ranking_system: str,
        ranking_type: str,
        field: str,
        subject: str,
        wait: int = 10,
        tries: int = 5,
    ):
        self.ranking_info = {
            "Ranking System": ranking_system,
            "Ranking Type": ranking_type,
            "Year": str(year),
            "Field": field,
            "Subject": subject,
        }

        self.wait = wait
        self.tries = tries

        self.file_name = "_".join(self.ranking_info.values()) + ".csv"
        self.file_path = Path(self.DOWNLOAD_DIR) / self.file_name
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def country_name_mapper(cls, country: str) -> str:
        return cls.COUNTRY_NAMES.get(country.lower(), country)

    def crawl(self):
        for i in range(self.tries):
            try:
                self._get_page()
                self._get_tbl()
                if len(self.urls) > 1:
                    self._tbl_merger(on_cols=self.merge_on_cols)
                self._csv_export()
            except ConnectionError:
                print(f"Waiting for {self.wait} seconds.")
                time.sleep(self.wait)
                continue

            break

    def _get_page(self) -> BeautifulSoup:
        """Requests a page for data extraction.

        Uses browser rendering if necessary.

        Raises:
            ConnectionError: If the request is not successful

        Returns:
            BeautifulSoup: Soup
        """
        session = HTMLSession()
        self.pages = []
        try:
            for url in self.urls:
                page = session.get(url, headers=self.headers)
                if page.status_code != 200:
                    raise ConnectionError(f"Error getting page: {url}")
                if self.use_js:
                    page.html.render()
                    self.pages.append(
                        BeautifulSoup(page.html.html, "html.parser")
                    )
                else:
                    self.pages.append(
                        BeautifulSoup(page.content, "html.parser")
                    )

                print(f"Downloaded page: {url}")
            return self.pages
        except Exception:
            pass
        finally:
            session.close()

    def _csv_export(self):
        """Exports a table to a .csv file."""
        with io.open(
            self.file_path, "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            writer.writerow(self.tbl_headers[0] + list(self.ranking_info))
            writer.writerows(
                row + list(self.ranking_info.values())
                for row in self.tbl_contents[0]
                if row
            )
            print(f"Saved file: {self.file_path}")
