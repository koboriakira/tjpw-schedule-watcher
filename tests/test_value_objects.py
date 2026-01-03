"""Tests for domain value objects."""

from datetime import date, datetime

import pytest

from tjpw_schedule_watcher.domain.value_objects import (
    Date,
    DetailUrl,
    ScrapeRange,
    TournamentName,
)


class TestTournamentName:
    """Tests for TournamentName value object."""

    def test_valid_name(self) -> None:
        """Test valid tournament name."""
        name = TournamentName(value="Test Tournament")
        assert name.value == "Test Tournament"

    def test_empty_name(self) -> None:
        """Test empty tournament name raises error."""
        with pytest.raises(ValueError):
            TournamentName(value="")

    def test_whitespace_name(self) -> None:
        """Test whitespace-only tournament name raises error."""
        with pytest.raises(ValueError):
            TournamentName(value="   ")


class TestDate:
    """Tests for Date value object."""

    def test_parse_with_start_time(self) -> None:
        """Test parsing date with start time."""
        date_str = "2023年10月9日(月)　開場13:00　開始14:00"
        date_obj = Date.from_string(date_str)

        assert date_obj.date_value == date(2023, 10, 9)
        assert date_obj.start_time == datetime(2023, 10, 9, 14, 0)
        assert date_obj.end_time == datetime(2023, 10, 9, 18, 0)

    def test_parse_with_door_time_only(self) -> None:
        """Test parsing date with door time only."""
        date_str = "2023年10月9日(月)　開場13:00"
        date_obj = Date.from_string(date_str)

        assert date_obj.date_value == date(2023, 10, 9)
        assert date_obj.start_time == datetime(2023, 10, 9, 13, 0)
        assert date_obj.end_time == datetime(2023, 10, 9, 17, 0)

    def test_parse_invalid_format(self) -> None:
        """Test parsing invalid date format raises error."""
        with pytest.raises(ValueError):
            Date.from_string("Invalid date")


class TestDetailUrl:
    """Tests for DetailUrl value object."""

    def test_valid_url(self) -> None:
        """Test valid detail URL."""
        url = DetailUrl(
            value="https://www.tjpw.jp/schedules/123",
            date=datetime(2023, 10, 9),
        )
        assert url.value == "https://www.tjpw.jp/schedules/123"
        assert url.date == datetime(2023, 10, 9)

    def test_empty_url(self) -> None:
        """Test empty URL raises error."""
        with pytest.raises(ValueError):
            DetailUrl(value="", date=datetime(2023, 10, 9))

    def test_invalid_url_format(self) -> None:
        """Test invalid URL format raises error."""
        with pytest.raises(ValueError):
            DetailUrl(value="not-a-url", date=datetime(2023, 10, 9))


class TestScrapeRange:
    """Tests for ScrapeRange value object."""

    def test_valid_range(self) -> None:
        """Test valid scrape range."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)
        range_obj = ScrapeRange(start_date=start, end_date=end)

        assert range_obj.start_date == start
        assert range_obj.end_date == end

    def test_invalid_range(self) -> None:
        """Test invalid scrape range (start after end) raises error."""
        start = datetime(2023, 12, 31)
        end = datetime(2023, 1, 1)

        with pytest.raises(ValueError):
            ScrapeRange(start_date=start, end_date=end)

    def test_default_range(self) -> None:
        """Test default scrape range."""
        range_obj = ScrapeRange.default(development=False)

        assert range_obj.start_date <= range_obj.end_date
        # Should be approximately 90 days
        delta = (range_obj.end_date - range_obj.start_date).days
        assert 89 <= delta <= 91

    def test_default_development_range(self) -> None:
        """Test default development scrape range."""
        range_obj = ScrapeRange.default(development=True)

        assert range_obj.start_date <= range_obj.end_date
        # Should be approximately 7 days
        delta = (range_obj.end_date - range_obj.start_date).days
        assert 6 <= delta <= 8
