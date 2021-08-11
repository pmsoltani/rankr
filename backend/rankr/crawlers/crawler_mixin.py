import time
from pathlib import Path
from typing import Callable, Dict, List, Union

import tqdm

from config import crwc
from rankr import db_models as d, repos as r, schemas as s
from utils import csv_export


class CrawlerMixin(object):
    """Common tools and settings across different ranking crawlers"""

    _get_page: Callable
    _get_tbl: Callable
    download_dir: Path
    processed_data: List[Dict[str, str]]
    url: str

    def __init__(
        self,
        year: Union[str, int],
        ranking_system: str,
        ranking_type: str,
        field: str,
        subject: str,
        wait: int = 10,
        tries: int = 5,
    ) -> None:
        # self.ranking_info is mainly used to enrich ranking tables with
        # additional metadata
        self.ranking_info: Dict[str, str] = {
            "ranking_system": ranking_system,
            "ranking_type": ranking_type,
            "year": str(year),
            "field": field,
            "subject": subject,
        }
        self.processed_data = []

        self.wait = wait
        self.tries = tries

        self.file_name = "_".join(self.ranking_info.values()) + ".csv"
        if "candidates" in self.url.lower():
            # In 2017 & 2018, Shanghai ranking separated their results
            # into two tables with slightly different structures.
            self.file_name = self.file_name.replace(".csv", "_candidates.csv")
        self.file_path = Path(self.download_dir) / self.file_name
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def crawl(self) -> None:
        """Provides the same interface for all ranking crawlers."""
        for i in range(self.tries):
            try:
                self._get_page()
                self._get_tbl()
                self._csv_export()
                print(f"Saved file: {self.file_path}")
            except ConnectionError:
                print(f"Waiting for {self.wait} seconds.")
                time.sleep(self.wait)
                continue

            break

    def _csv_export(self):
        return csv_export(file_path=self.file_path, data=self.processed_data)

    def crawl_and_process(
        self,
        institution_repo: r.InstitutionRepo,
        soup: Dict[str, Dict[str, str]],
    ):
        for i in range(self.tries):
            try:
                self._get_page()
                self._get_tbl()
            except ConnectionError:
                print(f"Waiting for {self.wait} seconds.")
                time.sleep(self.wait)
                continue

            break

        metric_types = crwc.RANKINGS["metrics"]
        non_metric_cols = crwc.RANKINGS["non_metrics"]

        matched_institutions = []
        fuzzy_matched_list = []
        not_matched_list = []

        for row in tqdm(self.processed_data):
            inst_info = {
                "raw_name": row["institution"],
                "country": row["country"],
                "url": row["url"],
                **self.ranking_info,
            }
            match = institution_repo.match_institution(
                institution_name=row["institution"],
                institution_url=row["url"],
                link_type=row["ranking_system"],
                country_name=row["country"],
                soup=soup,
            )
            db_institution, fuzzy_flag = match
            # could not match, or was matched before (with another institution)
            if not db_institution or db_institution in matched_institutions:
                not_matched_list.append(
                    {
                        "issue": "NOT MATCHED"
                        if not db_institution
                        else f"DOUBLE: {db_institution}",
                        **inst_info,
                    }
                )
                continue
            if fuzzy_flag:
                fuzzy_matched_list.append(
                    {
                        "fuzzy": db_institution.name,
                        "grid_id": db_institution.grid_id,
                        **inst_info,
                    }
                )

            link_types = [link.type.name for link in db_institution.links]
            if row["url"] and row["ranking_system"] not in link_types:
                link = s.LinkCreate(
                    institution_id=db_institution.id,
                    type=row["ranking_system"],
                    link=row["url"],
                )
                db_institution.links.append(d.Link(**link.dict()))

            for col in row:
                if col in non_metric_cols:
                    continue
                ranking = s.RankingCreate(
                    institution_id=db_institution.id,
                    ranking_system=row["ranking_system"],
                    ranking_type=row["ranking_type"],
                    year=row["year"],
                    field=row["field"],
                    subject=row["subject"],
                    metric=metric_types[row["ranking_system"]][col]["name"],
                    raw_value=row[col],
                    value_type=metric_types[row["ranking_system"]][col]["type"],
                    value=row[col],
                )
                db_institution.rankings.append(d.Ranking(**ranking.dict()))

            matched_institutions.append(db_institution)

        return (matched_institutions, not_matched_list, fuzzy_matched_list)
