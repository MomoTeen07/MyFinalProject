import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.services.football_service import get_standings


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
