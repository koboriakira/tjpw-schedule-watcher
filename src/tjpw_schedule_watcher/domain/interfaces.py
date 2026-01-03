"""Abstract classes and interfaces for the domain layer."""

from abc import ABC, abstractmethod

from tjpw_schedule_watcher.domain.models import TournamentSchedule
from tjpw_schedule_watcher.domain.value_objects import DetailUrl


class Scraper(ABC):
    """Abstract scraper interface."""

    @abstractmethod
    def get_detail_urls(self, year_month: str) -> list[DetailUrl]:
        """Get detail URLs from schedule list page.

        Args:
            year_month: Year and month in format "YYYYMM" (e.g., "202601")

        Returns:
            List of detail URLs
        """
        pass

    @abstractmethod
    def scrape_detail(self, url: str) -> TournamentSchedule:
        """Scrape detail page and get tournament schedule.

        Args:
            url: Detail page URL

        Returns:
            Tournament schedule
        """
        pass


class ScheduleExternalApi(ABC):
    """Abstract external API interface for schedule registration."""

    @abstractmethod
    def save(self, schedule: TournamentSchedule) -> None:
        """Save schedule to external API.

        Args:
            schedule: Tournament schedule to save
        """
        pass
