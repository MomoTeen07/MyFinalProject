from datetime import datetime, timedelta, timezone
from copy import deepcopy
from threading import Lock
from time import monotonic

import httpx
from fastapi import HTTPException

from app.core.config import settings

LEAGUES = {
    "PL": {"name": "Premier League", "country": "Angleterre"},
    "FL1": {"name": "Ligue 1", "country": "France"},
    "PD": {"name": "La Liga", "country": "Espagne"},
    "SA": {"name": "Serie A", "country": "Italie"},
    "BL1": {"name": "Bundesliga", "country": "Allemagne"},
    "CL": {"name": "Ligue des champions", "country": "Europe"},
}

MOCK_TEAMS = {
    "PL": [(57, "Arsenal"), (61, "Chelsea"), (64, "Liverpool"), (65, "Manchester City")],
    "FL1": [
        (524, "Paris Saint-Germain"),
        (516, "Olympique Lyonnais"),
        (522, "Olympique de Marseille"),
        (548, "AS Monaco"),
    ],
    "PD": [
        (81, "Barcelona"),
        (86, "Real Madrid"),
        (78, "Atlético de Madrid"),
        (90, "Real Valladolid"),
    ],
    "SA": [(98, "AC Milan"), (108, "Inter Milan"), (100, "Juventus"), (102, "Atalanta")],
    "BL1": [
        (5, "Bayern München"),
        (4, "Borussia Dortmund"),
        (18, "Hamburger SV"),
        (3, "Bayer Leverkusen"),
    ],
    "CL": [(81, "FC Barcelona"), (86, "Real Madrid"), (64, "Liverpool"), (5, "Bayern München")],
}
_RESPONSE_CACHE: dict[str, tuple[float, object]] = {}
_CACHE_LOCK = Lock()


def leagues():
    return [{"code": code, **league} for code, league in LEAGUES.items()]


def _headers():
    return {"X-Auth-Token": settings.football_api_token}


def _require_api_token():
    if not settings.football_api_token:
        raise HTTPException(
            status_code=503,
            detail="FOOTBALL_API_TOKEN is required when MOCK_FOOTBALL_API is disabled",
        )


def _fetch(path: str):
    _require_api_token()
    url = f"{settings.football_api_base_url}{path}"
    now = monotonic()
    ttl = settings.football_cache_ttl_seconds
    if ttl > 0:
        with _CACHE_LOCK:
            cached = _RESPONSE_CACHE.get(url)
            if cached and now - cached[0] < ttl:
                return deepcopy(cached[1])

    try:
        response = httpx.get(
            url,
            headers=_headers(),
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            retry_after = exc.response.headers.get("Retry-After", "60")
            raise HTTPException(
                status_code=503,
                detail="Football data provider rate limit reached. Please retry later.",
                headers={"Retry-After": retry_after},
            ) from exc
        raise HTTPException(
            status_code=502,
            detail=f"Football data API returned HTTP {exc.response.status_code}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Could not reach the football data API") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Football data API returned invalid JSON") from exc

    if ttl > 0:
        with _CACHE_LOCK:
            expired_urls = [key for key, (stored_at, _) in _RESPONSE_CACHE.items() if now - stored_at >= ttl]
            for expired_url in expired_urls:
                _RESPONSE_CACHE.pop(expired_url, None)
            if len(_RESPONSE_CACHE) >= 128:
                _RESPONSE_CACHE.pop(next(iter(_RESPONSE_CACHE)))
            _RESPONSE_CACHE[url] = (monotonic(), deepcopy(payload))
    return payload


def get_standings(code: str):
    if code not in LEAGUES:
        raise HTTPException(status_code=404, detail="Championship not found")

    if settings.mock_football_api:
        return [
            {
                "position": index + 1,
                "team": {"id": team_id, "name": name, "crest": ""},
                "playedGames": 10,
                "won": 7 - index,
                "draw": 2,
                "lost": 1 + index,
                "points": 23 - 2 * index,
            }
            for index, (team_id, name) in enumerate(MOCK_TEAMS[code])
        ]

    payload = _fetch(f"/competitions/{code}/standings")
    tables = payload.get("standings", [])
    overall_table = next((table for table in tables if table.get("type") == "TOTAL"), None)
    selected_table = overall_table or (tables[0] if tables else {})
    return selected_table.get("table", [])


def get_team(code: str, team_id: int):
    if code not in LEAGUES:
        raise HTTPException(status_code=404, detail="Championship not found")

    if settings.mock_football_api:
        team = next((item for item in MOCK_TEAMS[code] if item[0] == team_id), None)
        if team is None:
            raise HTTPException(status_code=404, detail="Team not found")
        return {
            "id": team[0],
            "name": team[1],
            "crest": "",
            "venue": "Football QA Stadium",
            "website": None,
        }

    return _fetch(f"/teams/{team_id}")


def get_matches(code: str):
    if code not in LEAGUES:
        raise HTTPException(status_code=404, detail="Championship not found")

    if settings.mock_football_api:
        teams = MOCK_TEAMS[code]
        now = datetime.now(timezone.utc)
        return [
            {
                "id": index + 1,
                "utcDate": (now + timedelta(days=7 * (index + 1))).isoformat(),
                "status": "SCHEDULED",
                "homeTeam": {"id": teams[0][0], "name": teams[0][1]},
                "awayTeam": {"id": teams[1][0], "name": teams[1][1]},
            }
            for index in range(3)
        ]

    return _fetch(f"/competitions/{code}/matches").get("matches", [])
