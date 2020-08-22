import csv
import io
import time
from pathlib import Path
from typing import Union


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
        if "candidates" in self.url.lower():
            self.file_name = self.file_name.replace(".csv", "_candidates.csv")
        self.file_path = Path(self.DOWNLOAD_DIR) / self.file_name
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def crawl(self):
        for i in range(self.tries):
            try:
                self._get_page()
                self._get_tbl()
                self._csv_export()
            except ConnectionError:
                print(f"Waiting for {self.wait} seconds.")
                time.sleep(self.wait)
                continue

            break

    def _csv_export(self):
        with io.open(
            self.file_path, "w", newline="", encoding="utf-8"
        ) as csv_file:
            dict_writer = csv.DictWriter(
                csv_file, self.processed_data[0].keys(), quoting=csv.QUOTE_ALL
            )
            dict_writer.writeheader()
            dict_writer.writerows(self.processed_data)
        print(f"Saved file: {self.file_path}")
