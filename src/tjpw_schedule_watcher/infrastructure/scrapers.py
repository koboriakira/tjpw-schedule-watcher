"""Schedule scraper implementation."""

import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By

from tjpw_schedule_watcher.domain.interfaces import Scraper
from tjpw_schedule_watcher.domain.models import TournamentSchedule
from tjpw_schedule_watcher.domain.value_objects import (
    Date,
    DetailUrl,
    Note,
    SeatType,
    TournamentName,
    Venue,
)
from tjpw_schedule_watcher.infrastructure.constants import (
    IGNORE_URLS,
    SCHEDULE_LIST_URL,
)
from tjpw_schedule_watcher.infrastructure.selenium_factory import SeleniumFactory


class ScheduleScraper:
    """Scraper for schedule list page."""

    def __init__(self) -> None:
        """Initialize scraper."""
        pass

    def get_detail_urls(self, year_month: str) -> list[DetailUrl]:
        """Get detail URLs from schedule list page.

        Args:
            year_month: Year and month in format "YYYYMM" (e.g., "202601")

        Returns:
            List of detail URLs
        """
        driver = SeleniumFactory.create()
        try:
            url = f"{SCHEDULE_LIST_URL}?date={year_month}"
            driver.get(url)

            # Wait for page load
            time.sleep(3)

            # Find all schedule link items
            items = driver.find_elements(By.CLASS_NAME, "ScheduleList_itemLink__DWrQV")

            detail_urls: list[DetailUrl] = []
            for item in items:
                try:
                    # Get href attribute
                    href = item.get_attribute("href")
                    if not href or "schedules" not in href or href in IGNORE_URLS:
                        continue

                    # Find parent item container to get date
                    parent = item.find_element(By.XPATH, "../..")
                    date_elem = parent.find_element(By.CLASS_NAME, "ScheduleList_date__Jv4_u")
                    date_text = date_elem.text  # e.g., "01/04"

                    # Parse date: "01/04" with year_month "202601" -> datetime
                    date_match = re.search(r"(\d{1,2})/(\d{1,2})", date_text)
                    if not date_match:
                        continue

                    year = int(year_month[:4])
                    month = int(date_match.group(1))
                    day = int(date_match.group(2))
                    dt = datetime(year, month, day)

                    detail_urls.append(DetailUrl(value=href, date=dt))
                except Exception:
                    # Skip invalid items
                    continue

            return detail_urls
        finally:
            driver.quit()


class ShowScraper:
    """Scraper for show detail page."""

    def __init__(self) -> None:
        """Initialize scraper."""
        pass

    def scrape_detail(self, url: str) -> TournamentSchedule:
        """Scrape detail page and get tournament schedule.

        Args:
            url: Detail page URL

        Returns:
            Tournament schedule
        """
        driver = SeleniumFactory.create()
        try:
            driver.get(url)

            # Wait for page load
            time.sleep(3)

            # Get tournament name from h1
            title_elem = driver.find_element(By.CLASS_NAME, "ArticleTemplate_articleTitle__6_43t")
            tournament_name_str = title_elem.text.strip()

            # Find table with event overview
            table = driver.find_element(By.CLASS_NAME, "ArticleEventOverview_table__jNOyC")
            rows = table.find_elements(By.CLASS_NAME, "ArticleEventOverview_row___VIw_")

            data: dict[str, str] = {}
            for row in rows:
                try:
                    head = row.find_element(By.CLASS_NAME, "ArticleEventOverview_head__H_jzM")
                    desc = row.find_element(By.CLASS_NAME, "ArticleEventOverview_description__iMYU1")

                    key = head.text.strip()
                    value = desc.text.strip()

                    data[key] = value
                except Exception:
                    continue

            # Create domain objects
            tournament_name = TournamentName(value=tournament_name_str)
            date_str = data.get("日時", "")
            if not date_str:
                raise ValueError(f"Cannot find date information in {url}")
            date = Date.from_string(date_str)
            venue = Venue(value=data.get("会場", "Unknown Venue"))

            # Seat type and note are optional - try to find them in content sections
            seat_type = SeatType(value="")
            note = Note(value="")

            return TournamentSchedule(
                url=url,
                tournament_name=tournament_name,
                date=date,
                venue=venue,
                seat_type=seat_type,
                note=note,
            )
        finally:
            driver.quit()


class SeleniumScraper(Scraper):
    """Selenium-based scraper implementation."""

    def __init__(self) -> None:
        """Initialize scraper."""
        self.schedule_scraper = ScheduleScraper()
        self.show_scraper = ShowScraper()

    def get_detail_urls(self, year_month: str) -> list[DetailUrl]:
        """Get detail URLs from schedule list page.

        Args:
            year_month: Year and month in format "YYYYMM" (e.g., "202601")

        Returns:
            List of detail URLs
        """
        return self.schedule_scraper.get_detail_urls(year_month)

    def scrape_detail(self, url: str) -> TournamentSchedule:
        """Scrape detail page and get tournament schedule.

        Args:
            url: Detail page URL

        Returns:
            Tournament schedule
        """
        return self.show_scraper.scrape_detail(url)
