"""Value objects for the domain layer."""

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class TournamentName:
    """Tournament name value object."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Tournament name cannot be empty")


@dataclass(frozen=True)
class Venue:
    """Venue value object."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Venue cannot be empty")


@dataclass(frozen=True)
class SeatType:
    """Seat type value object."""

    value: str


@dataclass(frozen=True)
class Note:
    """Note value object."""

    value: str


@dataclass(frozen=True)
class Date:
    """Date value object with parsing logic.

    Parses date strings like: "2023年10月9日(月)　開場13:00　開始14:00"
    """

    raw_value: str
    date_value: date
    start_time: datetime
    end_time: datetime

    @classmethod
    def from_string(cls, date_str: str) -> "Date":
        """Parse date string and create Date object.

        Args:
            date_str: Date string like "2023年10月9日(月)　開場13:00　開始14:00"

        Returns:
            Date object

        Raises:
            ValueError: If date string cannot be parsed
        """
        # Extract date part: "2023年10月9日"
        date_match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
        if not date_match:
            raise ValueError(f"Cannot parse date from: {date_str}")

        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))
        date_value = date(year, month, day)

        # Extract time: prioritize "開始" over "開場"
        start_match = re.search(r"開始[　\s]*(\d{1,2}):(\d{2})", date_str)
        if start_match:
            hour = int(start_match.group(1))
            minute = int(start_match.group(2))
        else:
            # Try "開場" if "開始" not found
            door_match = re.search(r"開場[　\s]*(\d{1,2}):(\d{2})", date_str)
            if door_match:
                hour = int(door_match.group(1))
                minute = int(door_match.group(2))
            else:
                # Default to 14:00 if no time found
                hour = 14
                minute = 0

        start_time = datetime(year, month, day, hour, minute)
        # End time is start time + 4 hours
        end_time = start_time + timedelta(hours=4)

        return cls(
            raw_value=date_str,
            date_value=date_value,
            start_time=start_time,
            end_time=end_time,
        )


@dataclass(frozen=True)
class DetailUrl:
    """Detail URL value object."""

    value: str
    date: datetime

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Detail URL cannot be empty")
        if not self.value.startswith("http"):
            raise ValueError("Detail URL must start with http")


@dataclass(frozen=True)
class ScrapeRange:
    """Scrape range value object."""

    start_date: datetime
    end_date: datetime

    def __post_init__(self) -> None:
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")

    @classmethod
    def default(cls, development: bool = False) -> "ScrapeRange":
        """Create default scrape range.

        Args:
            development: If True, use 7 days range, otherwise 90 days

        Returns:
            ScrapeRange with default values
        """
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days = 7 if development else 90
        end_date = start_date + timedelta(days=days)
        return cls(start_date=start_date, end_date=end_date)
