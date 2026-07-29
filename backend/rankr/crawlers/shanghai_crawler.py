from pathlib import Path
from typing import Any

from playwright.sync_api import Playwright, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import shac
from rankr import schemas as s
from rankr.crawlers.crawler_mixin import CrawlerMixin


class ShanghaiCrawler(CrawlerMixin):
    # The ranking pages are a Nuxt app whose table is rendered from a payload
    # holding every institution at once, so the whole table comes from a single
    # navigation rather than clicking through the pager.
    NUXT_DATA = "() => window.__NUXT__.data[0]"
    NUXT_READY = """
        () => {
            const data = window.__NUXT__ && window.__NUXT__.data;
            const page = data && data[0];
            return Boolean(page && page.univList && page.univList.length);
        }
    """
    GOTO_TIMEOUT = 120_000
    # The payload lands right after the document does, so a page still without
    # one is a page that has none; a moved ranking, or a url now serving the
    # 404 view. Worth failing quickly and legibly instead of waiting it out.
    HYDRATE_TIMEOUT = 30_000

    def __init__(self, url: str, driver_path: str = "chromedriver", **kwargs) -> None:
        self.url = url
        self.download_dir = shac.DOWNLOAD_DIR

        self.driver_path = driver_path
        self.raw_data: dict[str, Any] = {}

        super().__init__(**kwargs)

    def _launch_browser(self, playwright: Playwright):
        launch_kwargs: dict[str, Any] = {
            "headless": True,
            "args": ["--disable-notifications"],
        }

        driver_path = Path(self.driver_path)
        if driver_path.exists():
            launch_kwargs["executable_path"] = str(driver_path)
        else:
            launch_kwargs["channel"] = "msedge"

        return playwright.chromium.launch(**launch_kwargs)

    def _get_page(self) -> int:
        """Retrieves the ranking table's data from the page's Nuxt payload.

        The table used to be paged through in the browser, one click per
        metric per page. It is now rendered from `window.__NUXT__`, which
        carries every institution and every indicator, so one navigation is
        enough. The payload is fetched after the document loads, hence the
        wait rather than reading it straight after `goto`.

        Returns:
            int: The number of institutions found

        Raises:
            RuntimeError: If the page held no ranking data
        """
        with sync_playwright() as playwright:
            browser = self._launch_browser(playwright)
            try:
                page = browser.new_page()
                page.goto(
                    self.url, wait_until="domcontentloaded", timeout=self.GOTO_TIMEOUT
                )
                try:
                    page.wait_for_function(
                        self.NUXT_READY, timeout=self.HYDRATE_TIMEOUT
                    )
                except PlaywrightTimeoutError as exc:
                    raise RuntimeError(
                        f"Unable to find the ranking table data: {self.url}"
                    ) from exc
                self.raw_data = page.evaluate(self.NUXT_DATA)
            finally:
                browser.close()

        if not self.raw_data.get("univList"):
            raise RuntimeError(f"Unable to find the ranking table data: {self.url}")

        return len(self.raw_data["univList"])

    def _get_tbl(self) -> list[dict[str, str]]:
        """Finds the ranking table within the page & extracts the data.

        Returns:
            list[dict[str, str]]: Table data as a list of dictionaries
        """
        # Indicators are keyed by a code that changes every year (Alumni was
        # "159" in 2024 and "165" in 2025), so the names come from `indList`.
        metrics: dict[str, str] = {}
        for indicator in self.raw_data.get("indList") or []:
            col_name = shac.FIELDS.get(str(indicator.get("nameEn", "")).lower())
            if not col_name:  # ignoring irrelevant data
                continue
            metrics[str(indicator["code"])] = col_name

        self.processed_data = [
            self._process_institution(institution, metrics)
            for institution in self.raw_data["univList"]
        ]
        return self.processed_data

    def _process_institution(
        self, institution: dict[str, Any], metrics: dict[str, str]
    ) -> dict[str, str]:
        """Flattens one institution of the payload into a table row.

        Args:
            institution (dict[str, Any]): One entry of the payload's "univList"
            metrics (dict[str, str]): Indicator code -> column name

        Returns:
            dict[str, str]: The processed row
        """
        slug = str(institution.get("univUp") or "").strip("/")
        values: dict[str, str] = {
            "rank": self._clean(institution.get("ranking")),
            # The canonical path is now /universities/<slug>, but it still
            # resolves under the /institution/<slug> the earlier years were
            # crawled with, which is what the stored links are matched on.
            "url": f"{shac.BASE_URL.rstrip('/')}/institution/{slug}" if slug else "",
            "institution": self._clean(institution.get("univNameEn")),
            "country": self._get_country(institution),
            "national rank": self._clean(institution.get("regionRanking")),
            "total score": self._clean(institution.get("score")),
        }

        indicators: dict[str, Any] = institution.get("indData") or institution
        for code, col_name in metrics.items():
            values[col_name] = self._clean(indicators.get(code))

        return {**values, **self.ranking_info}

    @staticmethod
    def _get_country(institution: dict[str, Any]) -> str:
        """Resolves an institution's country.

        The two-letter code behind the flag is preferred over the payload's
        own region name, since that name is sometimes a region rather than a
        country (e.g. "China-Mainland").

        Args:
            institution (dict[str, Any]): One entry of the payload's "univList"

        Returns:
            str: The resolved country name, or "" if it could not be resolved
        """
        region = str(institution.get("region") or "").strip()
        country_code = str(institution.get("regionLogo") or "").strip()

        for kwargs in (
            {"country": "", "country_code": country_code},
            {"country": region},
        ):
            if not any(kwargs.values()):
                continue
            try:
                return s.CountryCreate(**kwargs).country
            except (KeyError, ValueError):
                continue

        return ""

    @staticmethod
    def _clean(value: Any) -> str:
        """Renders a raw payload value as a table value.

        Args:
            value (Any): The raw value

        Returns:
            str: The cleaned value
        """
        if value is None:
            return ""
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, int | float):
            # Scores are numbers in the payload but shown to one decimal on
            # the site, which is the form the earlier years were crawled in.
            return f"{value:.1f}"
        return str(value).strip()
