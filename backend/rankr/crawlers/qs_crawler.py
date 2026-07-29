import json
import re
import time
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag

from config import qsc
from rankr import schemas as s
from rankr.crawlers.crawler_mixin import CrawlerMixin


class QSCrawler(CrawlerMixin):
    # The rankings endpoint pages its results. This is large enough to pull any
    # current table in one request, but `total_pages` is still followed in case
    # the server starts capping the page size.
    ITEMS_PER_PAGE = 1000

    def __init__(self, url: str, **kwargs) -> None:
        self.url = url
        self.download_dir = qsc.DOWNLOAD_DIR
        self.node_id = ""
        super().__init__(**kwargs)

    def _get_page(self) -> str:
        """Retrieves the URL of raw json data for the ranking table.

        QS ranking tables (in https://www.topuniversities.com/) each
        have a unique "node number". For example, QS World University
        Rankings has the following short-link in the page's metadata:

        https://www.topuniversities.com/node/946820

        Newer tables are served by a paginated REST endpoint keyed on
        that node number:

        https://www.topuniversities.com/rankings/endpoint?nid=946820&...

        Older tables were dumped to a static json file instead. QS has
        stopped generating those for the latest ranking, and the 2026 one
        is missing all of its indicator columns, so the endpoint is
        preferred and the static file is only a fallback:

        https://www.topuniversities.com/
        sites/default/files/qs-rankings-data/en/946820_indicators.txt

        So all we have to do is to find this node number and retrieve the json.

        Returns:
            str: The url for the ranking table data
        """
        html_page = self._request(self.url)
        if html_page is None:
            raise RuntimeError(f"Unable to retrieve the QS rankings page: {self.url}")

        html_soup = BeautifulSoup(html_page.content, "html.parser")
        node_tag = html_soup.find("article", {"data-history-node-id": True})
        node_id = None
        if isinstance(node_tag, Tag):
            node_id = node_tag.get("data-history-node-id")

        for pattern in (
            r'data-history-node-id="(\d+)"',
            r'qs_rankings_rest_api"\s*:\s*{\s*"nid"\s*:\s*"(\d+)"',
        ):
            if isinstance(node_id, str):
                break
            node_id_match = re.search(pattern, html_page.text)
            if node_id_match:
                node_id = node_id_match.group(1)

        if not isinstance(node_id, str):
            raise RuntimeError("Unable to find the QS rankings node id for this page")

        self.node_id = node_id
        self.json_url = self._endpoint_url()
        return self.json_url

    def _request(self, url: str) -> requests.Response | None:
        """GETs a URL, retrying when QS rejects the request.

        Args:
            url (str): The URL to retrieve

        Returns:
            requests.Response | None: The response, or None if every try failed
        """
        for attempt in range(self.tries):
            response = requests.get(url, headers=qsc.HEADERS, timeout=60)
            if response.ok:
                return response
            time.sleep(self.wait * 2**attempt)

        return None

    def _endpoint_url(self, page: int = 0) -> str:
        """Builds a URL for a single page of the rankings endpoint.

        "tab=indicators" is what makes the response carry the per-indicator
        scores rather than the overall score alone.

        Args:
            page (int): The zero-based page number. Defaults to 0.

        Returns:
            str: The url for that page of the ranking table data
        """
        query: dict[str, Any] = {
            "nid": self.node_id,
            "page": page,
            "items_per_page": self.ITEMS_PER_PAGE,
            "tab": "indicators",
            "sort_by": "rank",
            "order_by": "asc",
        }
        query_string = "&".join(f"{key}={value}" for key, value in query.items())
        return f"{qsc.BASE_URL.rstrip('/')}/rankings/endpoint?{query_string}"

    def _legacy_url(self) -> str:
        """Builds the URL of the static json file for older rankings.

        Returns:
            str: The url for the ranking table data
        """
        return (
            qsc.BASE_URL.rstrip("/")
            + "/sites/default/files/qs-rankings-data/en"
            + f"/{self.node_id}_indicators.txt"
        )

    def _get_tbl(self) -> list[dict[str, str]]:
        """Processes raw ranking data into a list of dictionaries.

        Returns:
            list[dict[str, str]]: Processed ranking data to be exported
        """
        score_nodes = self._get_score_nodes()
        if score_nodes is None:
            # Rankings too old to be served by the endpoint.
            self.json_url = self._legacy_url()
            return self._get_legacy_tbl()

        rows = [self._process_score_node(node) for node in score_nodes]
        self.processed_data = self._align_columns(rows)
        return self.processed_data

    def _get_score_nodes(self) -> list[dict[str, Any]] | None:
        """Collects every institution from the rankings endpoint.

        An unreachable endpoint is raised rather than fallen back on: the
        static json file is missing its indicator columns for the rankings
        the endpoint serves, so quietly reaching for it would turn a blocked
        request into a table that looks complete but has lost every score.

        Returns:
            list[dict[str, Any]] | None: The institutions, or None when the
                endpoint holds no data for this ranking

        Raises:
            RuntimeError: If the endpoint could not be read
        """
        score_nodes: list[dict[str, Any]] = []
        page = 0
        while True:
            url = self._endpoint_url(page)
            response = self._request(url)
            if response is None:
                raise RuntimeError(f"Unable to retrieve the QS ranking data: {url}")
            try:
                raw_data = response.json()
            except ValueError as exc:
                raise RuntimeError(
                    f"The QS rankings endpoint did not return json: {url}"
                ) from exc

            nodes = raw_data.get("score_nodes")
            if not nodes:
                # Rankings too old to be served by the endpoint.
                return score_nodes or None
            score_nodes.extend(nodes)

            page += 1
            if page >= int(raw_data.get("total_pages") or 1):
                return score_nodes

    def _process_score_node(self, node: dict[str, Any]) -> dict[str, str]:
        """Flattens one institution from the endpoint into a table row.

        Args:
            node (dict[str, Any]): One entry of the endpoint's "score_nodes"

        Returns:
            dict[str, str]: The processed row
        """
        href = self._clean(node.get("path")).lstrip("/")
        values: dict[str, str] = {
            "rank": self._clean(node.get("rank_display")),
            "institution": self._clean(node.get("title")),
            "url": f"{qsc.BASE_URL.rstrip('/')}/{href}" if href else "",
            "overall score": self._clean(node.get("overall_score")),
        }

        country = self._clean(node.get("country"))
        try:
            values["country"] = s.CountryCreate(country=country).country
        except KeyError:
            values["country"] = country

        # Indicators are grouped by methodology pillar (e.g. "Employability"),
        # and only the ones we keep a metric for are of interest.
        scores: dict[str, list[dict[str, Any]]] = node.get("scores") or {}
        for indicators in scores.values():
            for indicator in indicators:
                indicator_name = self._clean(indicator.get("indicator_name"))
                col_name = qsc.FIELDS.get(indicator_name.lower())
                if not col_name:  # ignoring irrelevant data
                    continue
                values[col_name] = self._clean(indicator.get("score"))

        return {**values, **self.ranking_info}

    @staticmethod
    def _clean(value: Any) -> str:
        """Normalises a raw endpoint value, treating "n/a" as missing.

        Args:
            value (Any): The raw value

        Returns:
            str: The cleaned value
        """
        value = str(value if value is not None else "").strip()
        return "" if value.lower() == "n/a" else value

    @staticmethod
    def _align_columns(rows: list[dict[str, str]]) -> list[dict[str, str]]:
        """Gives every row the same columns, in first-seen order.

        The csv export takes its header from the first row, so a row that
        reports an indicator the first one lacks would otherwise break it.

        Args:
            rows (list[dict[str, str]]): The processed rows

        Returns:
            list[dict[str, str]]: The rows, sharing one set of columns
        """
        columns = dict.fromkeys(col for row in rows for col in row)
        return [{col: row.get(col, "") for col in columns} for row in rows]

    def _get_legacy_tbl(self) -> list[dict[str, str]]:
        """Processes the static json file of older rankings.

        Returns:
            list[dict[str, str]]: Processed ranking data to be exported
        """
        page = self._request(self.json_url)
        if page is None:
            raise RuntimeError(
                f"Unable to retrieve the QS ranking data: {self.json_url}"
            )
        raw_data = json.loads(page.text)

        # Column names are separated from actual data.
        columns: dict[str, str] = {}
        for col in raw_data["columns"]:
            col_disp = BeautifulSoup(col["title"], "html.parser").text
            col_name = qsc.FIELDS.get(col_disp.lower())
            if not col_name:  # ignoring irrelevant data
                if "university" in col_disp.lower():
                    columns[col["data"]] = qsc.FIELDS["university"]
                continue
            columns[col["data"]] = col_name

        # processing raw_data
        processed_data: list[dict[str, str]] = []
        for row in raw_data["data"]:
            values: dict[str, str] = {}
            for col in row:
                if col not in columns:
                    continue

                # None values make BeautifulSoup raise exception.
                row[col] = "" if not row[col] else row[col]
                value = BeautifulSoup(row[col], "html.parser")
                if columns[col] == "country":
                    try:
                        country = s.CountryCreate(country=value.text)
                        values[columns[col]] = country.country
                        continue
                    except KeyError:
                        pass
                if columns[col] == "institution":
                    a_tag = value.find("a")
                    assert isinstance(a_tag, Tag)
                    href = a_tag.get("href")
                    assert isinstance(href, str)
                    url = f"{qsc.BASE_URL.rstrip('/')}/{href.lstrip('/')}"
                    values["url"] = url
                    values[columns[col]] = value.text.strip()
                    continue

                values[columns[col]] = value.text.strip()

            processed_data.append({**values, **self.ranking_info})

        self.processed_data = processed_data
        return self.processed_data
