"""Use case for scraping TJPW schedule."""

import time
from collections.abc import Sequence
from datetime import datetime

from tjpw_schedule_watcher.domain.interfaces import (
    ScheduleExternalApi,
    Scraper,
)
from tjpw_schedule_watcher.domain.value_objects import ScrapeRange


class ScrapeTjpw:
    """Use case for scraping TJPW schedule and saving to external APIs."""

    def __init__(
        self,
        scraper: Scraper,
        external_apis: Sequence[ScheduleExternalApi],
    ) -> None:
        """Initialize use case.

        Args:
            scraper: Scraper implementation
            external_apis: List of external API implementations
        """
        self.scraper = scraper
        self.external_apis = external_apis

    def execute(self, scrape_range: ScrapeRange) -> None:
        """Execute scraping and saving to external APIs.

        Args:
            scrape_range: Date range to scrape
        """
        # Generate year-month list
        year_months = self._generate_year_months(
            scrape_range.start_date, scrape_range.end_date
        )

        # Scrape schedule list for each month
        all_detail_urls = []
        for year_month in year_months:
            print(f"Scraping schedule list for {year_month}...")
            detail_urls = self.scraper.get_detail_urls(year_month)
            all_detail_urls.extend(detail_urls)
            time.sleep(1)  # Avoid overwhelming the server

        # Filter URLs within date range
        filtered_urls = [
            url
            for url in all_detail_urls
            if scrape_range.start_date <= url.date <= scrape_range.end_date
        ]

        print(f"Found {len(filtered_urls)} schedules to scrape")

        # Scrape each detail page
        for i, url in enumerate(filtered_urls, 1):
            print(f"Scraping {i}/{len(filtered_urls)}: {url.value}")

            try:
                schedule = self.scraper.scrape_detail(url.value)

                # Save to all external APIs
                for api in self.external_apis:
                    try:
                        api.save(schedule)
                        print(f"  Saved to {api.__class__.__name__}")
                    except Exception as e:
                        print(f"  Failed to save to {api.__class__.__name__}: {e}")

            except Exception as e:
                print(f"  Failed to scrape: {e}")

            # Wait 3 seconds before next request (as per spec)
            if i < len(filtered_urls):
                time.sleep(3)

        print("Scraping completed!")

    def _generate_year_months(
        self, start_date: datetime, end_date: datetime
    ) -> list[str]:
        """Generate list of year-month strings.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of year-month strings in format "YYYYMM"
        """
        year_months = []
        current = start_date

        while current <= end_date:
            year_month = current.strftime("%Y%m")
            if year_month not in year_months:
                year_months.append(year_month)

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return year_months
