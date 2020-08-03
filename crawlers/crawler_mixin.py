import csv
import io
import time

from bs4 import BeautifulSoup
from requests_html import HTMLSession


class CrawlerMixin(object):
    @classmethod
    def country_name_mapper(cls, country: str) -> str:
        return cls.COUNTRY_NAMES.get(country.lower(), country)

    def crawl(self, use_merger: bool = False):
        for i in range(self.tries):
            try:
                self._get_page()
                self._get_tbl()
                if use_merger:
                    self._tbl_merger(on_cols=self.merge_on_cols)
                self._csv_export()
            except ConnectionError as exc:
                print(exc, type(exc))
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
        urls = [self.url / path for path in self.url_paths]
        self.pages = []
        try:
            for url in urls:
                page = session.get(url, headers=self.headers)
                if page.status_code != 200:
                    raise ConnectionError(f"Error getting page: {url}")
                if self.javascript:
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
            writer.writerow(self.tbl_headers + ["Year", "Field", "Subject"])
            writer.writerows(
                row + [self.year, self.field, self.subject]
                for row in self.tbl_contents
                if row
            )
            print(f"Saved file: {self.file_path}")
