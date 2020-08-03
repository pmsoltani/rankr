import csv
import io
import time

from bs4 import BeautifulSoup
from requests_html import HTMLSession


class CrawlerMixin(object):
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
        row_extension = {
            "Ranking System": self.ranking_system,
            "Ranking Type": self.ranking_type,
            "Year": self.year,
            "Field": self.field,
            "Subject": self.subject,
        }
        with io.open(
            self.file_path, "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            writer.writerow(self.tbl_headers + list(row_extension))
            writer.writerows(
                row + list(row_extension.values())
                for row in self.tbl_contents
                if row
            )
            print(f"Saved file: {self.file_path}")
