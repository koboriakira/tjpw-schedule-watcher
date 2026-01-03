"""Tests for domain models."""


from tjpw_schedule_watcher.domain.models import TournamentSchedule
from tjpw_schedule_watcher.domain.value_objects import (
    Date,
    Note,
    SeatType,
    TournamentName,
    Venue,
)


class TestTournamentSchedule:
    """Tests for TournamentSchedule model."""

    def test_to_google_calendar_dict(self) -> None:
        """Test converting to Google Calendar format."""
        date_str = "2023年10月9日(月)　開場13:00　開始14:00"
        schedule = TournamentSchedule(
            url="https://www.tjpw.jp/schedules/123",
            tournament_name=TournamentName(value="Test Tournament"),
            date=Date.from_string(date_str),
            venue=Venue(value="Test Venue"),
            seat_type=SeatType(value="全席指定"),
            note=Note(value="Test Note"),
        )

        result = schedule.to_google_calendar_dict()

        assert result["category"] == "東京女子"
        assert result["title"] == "Test Tournament"
        assert result["start"] == "2023-10-09T14:00:00"
        assert result["end"] == "2023-10-09T18:00:00"
        assert "https://www.tjpw.jp/schedules/123" in result["detail"]
        assert "Test Venue" in result["detail"]
        assert "全席指定" in result["detail"]
        assert "Test Note" in result["detail"]

    def test_to_notion_dict(self) -> None:
        """Test converting to Notion format."""
        date_str = "2023年10月9日(月)　開場13:00　開始14:00"
        schedule = TournamentSchedule(
            url="https://www.tjpw.jp/schedules/123",
            tournament_name=TournamentName(value="Test Tournament"),
            date=Date.from_string(date_str),
            venue=Venue(value="Test Venue"),
            seat_type=SeatType(value="全席指定"),
            note=Note(value="Test Note"),
        )

        result = schedule.to_notion_dict()

        assert result["url"] == "https://www.tjpw.jp/schedules/123"
        assert result["title"] == "Test Tournament"
        assert result["date"] == "2023-10-09"
        assert result["promotion"] == "東京女子プロレス"
        assert result["tags"] == []
