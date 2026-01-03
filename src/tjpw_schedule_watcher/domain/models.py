"""Domain models."""

from dataclasses import dataclass

from tjpw_schedule_watcher.domain.value_objects import (
    Date,
    Note,
    SeatType,
    TournamentName,
    Venue,
)


@dataclass(frozen=True)
class TournamentSchedule:
    """Tournament schedule domain model."""

    url: str
    tournament_name: TournamentName
    date: Date
    venue: Venue
    seat_type: SeatType
    note: Note

    def to_google_calendar_dict(self) -> dict[str, str]:
        """Convert to Google Calendar API format.

        Returns:
            Dictionary for Google Calendar API
        """
        return {
            "category": "東京女子",
            "title": self.tournament_name.value,
            "start": self.date.start_time.isoformat(),
            "end": self.date.end_time.isoformat(),
            "detail": f"{self.url}\n\n{self.venue.value}\n\n{self.seat_type.value}\n\n{self.note.value}",
        }

    def to_notion_dict(self) -> dict[str, str | list[str]]:
        """Convert to Notion API format.

        Returns:
            Dictionary for Notion API
        """
        return {
            "url": self.url,
            "title": self.tournament_name.value,
            "date": self.date.date_value.isoformat(),
            "promotion": "東京女子プロレス",
            "tags": [],
        }
