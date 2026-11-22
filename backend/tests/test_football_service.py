import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.services.football_service import get_match, get_matches, get_standings, leagues


def test_real_data_mode_requires_a_token(monkeypatch):
    monkeypatch.setattr(settings, "mock_football_api", False)
    monkeypatch.setattr(settings, "football_api_token", "")

    with pytest.raises(HTTPException) as exc_info:
        get_standings("PL")

    assert exc_info.value.status_code == 503


def test_mock_mode_remains_available_for_local_development(monkeypatch):
    monkeypatch.setattr(settings, "mock_football_api", True)

    standings = get_standings("PL")

    assert len(standings) == 4
    assert standings[0]["team"]["name"] == "Arsenal"


def test_champions_league_is_available():
    assert "CL" in {league["code"] for league in leagues()}


def test_mock_matches_are_paginated(monkeypatch):
    monkeypatch.setattr(settings, "mock_football_api", True)

    payload = get_matches("PL", page=1, page_size=2)

    assert payload["total"] == 6
    assert payload["total_pages"] == 3
    assert payload["page"] == 1
    assert payload["page_size"] == 2
    assert len(payload["items"]) == 2
    assert [match["id"] for match in payload["items"]] == [1, 2]


def test_mock_matches_filters_and_sort(monkeypatch):
    monkeypatch.setattr(settings, "mock_football_api", True)

    finished = get_matches("PL", page_size=100, status="FINISHED")
    assert finished["total"] == 2
    assert all(match["status"] == "FINISHED" for match in finished["items"])

    descending = get_matches("PL", page_size=100, sort="date_desc")
    dates = [match["utcDate"] for match in descending["items"]]
    assert dates == sorted(dates, reverse=True)

    team_id = finished["items"][0]["homeTeam"]["id"]
    by_team = get_matches("PL", page_size=100, team_id=team_id)
    assert by_team["items"]
    assert all(
        team_id in (match["homeTeam"]["id"], match["awayTeam"]["id"])
        for match in by_team["items"]
    )


def test_mock_matches_page_beyond_last_is_empty(monkeypatch):
    monkeypatch.setattr(settings, "mock_football_api", True)

    payload = get_matches("PL", page=4, page_size=2)

    assert payload["items"] == []
    assert payload["total_pages"] == 3


def test_mock_match_detail_covers_the_whole_calendar(monkeypatch):
    monkeypatch.setattr(settings, "mock_football_api", True)

    assert get_match(6)["id"] == 6

    with pytest.raises(HTTPException) as exc_info:
        get_match(7)

    assert exc_info.value.status_code == 404
