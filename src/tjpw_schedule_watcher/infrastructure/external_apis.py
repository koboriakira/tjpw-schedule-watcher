"""External API implementations for schedule registration."""

import os

import requests

from tjpw_schedule_watcher.domain.interfaces import ScheduleExternalApi
from tjpw_schedule_watcher.domain.models import TournamentSchedule


class ScheduleGoogleCalendarApi(ScheduleExternalApi):
    """Google Calendar API implementation (via Lambda)."""

    def __init__(self) -> None:
        """Initialize API client."""
        self.api_domain = os.environ.get("LAMBDA_GOOGLE_CALENDAR_API_DOMAIN", "")
        if not self.api_domain:
            raise ValueError("LAMBDA_GOOGLE_CALENDAR_API_DOMAIN is not set")

    def save(self, schedule: TournamentSchedule) -> None:
        """Save schedule to Google Calendar.

        Args:
            schedule: Tournament schedule to save
        """
        data = schedule.to_google_calendar_dict()

        try:
            response = requests.post(
                self.api_domain + "schedule",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to save to Google Calendar: {e}") from e


class ScheduleNotionApi(ScheduleExternalApi):
    """Notion API implementation."""

    def __init__(self) -> None:
        """Initialize API client."""
        self.api_domain = os.environ.get("LAMBDA_NOTION_API_DOMAIN", "")
        self.notion_secret = os.environ.get("NOTION_SECRET", "")

        if not self.api_domain:
            raise ValueError("LAMBDA_NOTION_API_DOMAIN is not set")
        if not self.notion_secret:
            raise ValueError("NOTION_SECRET is not set")

    def save(self, schedule: TournamentSchedule) -> None:
        """Save schedule to Notion.

        Args:
            schedule: Tournament schedule to save
        """
        data = schedule.to_notion_dict()

        try:
            response = requests.post(
                self.api_domain,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.notion_secret}",
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to save to Notion: {e}") from e


class NullScheduleExternalApi(ScheduleExternalApi):
    """Null implementation for testing (does nothing)."""

    def save(self, schedule: TournamentSchedule) -> None:
        """Do nothing.

        Args:
            schedule: Tournament schedule (ignored)
        """
        pass
