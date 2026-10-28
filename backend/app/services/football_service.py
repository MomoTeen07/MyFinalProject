from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException
from app.core.config import settings

LEAGUES = {
    "PL": {"name": "Premier League", "country": "England"},
    "FL1": {"name": "Ligue 1", "country": "France"},
    "PD": {"name": "La Liga", "country": "Spain"},
    "SA": {"name": "Serie A", "country": "Italy"},
    "BL1": {"name": "Bundesliga", "country": "Germany"},
    "CL": {"name": "Ligue des champions", "country": "Europe"},
}
MOCK_TEAMS = {
    "PL": [(57,"Arsenal"),(61,"Chelsea"),(64,"Liverpool"),(65,"Manchester City")],
    "FL1": [(524,"Paris Saint-Germain"),(516,"Olympique Lyonnais"),(522,"Olympique de Marseille"),(548,"AS Monaco")],
    "PD": [(81,"Barcelona"),(86,"Real Madrid"),(78,"Atlético de Madrid"),(90,"Real Valladolid")],
    "SA": [(98,"AC Milan"),(108,"Inter Milan"),(100,"Juventus"),(102,"Atalanta")],
    "BL1": [(5,"Bayern München"),(4,"Borussia Dortmund"),(18,"Hamburger SV"),(3,"Bayer Leverkusen")],
    "CL": [(81,"FC Barcelona"),(86,"Real Madrid"),(64,"Liverpool"),(5,"Bayern München")],
}

def leagues():
    return [{"code": k, **v} for k,v in LEAGUES.items()]

def _headers():
    return {"X-Auth-Token": settings.football_api_token}

def _require_api_token():
    if not settings.football_api_token:
        raise HTTPException(503, "FOOTBALL_API_TOKEN is required when MOCK_FOOTBALL_API is disabled")


def _fetch(path: str):
    _require_api_token()
    try:
        response = httpx.get(
            f"{settings.football_api_base_url}{path}",
            headers=_headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"Football data API returned HTTP {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise HTTPException(502, "Could not reach the football data API") from exc
    except ValueError as exc:
        raise HTTPException(502, "Football data API returned invalid JSON") from exc

def get_standings(code: str):
    if code not in LEAGUES:
        raise HTTPException(404, "Championship not found")
    if settings.mock_football_api:
        return [
            {"position": i + 1, "team": {"id": team_id, "name": name, "crest": ""},
             "playedGames": 10, "won": 7 - i, "draw": 2, "lost": 1 + i, "points": 23 - 2 * i}
            for i, (team_id, name) in enumerate(MOCK_TEAMS[code])
        ]
    payload = _fetch(f"/competitions/{code}/standings")
    tables = payload.get("standings", [])
    overall = next((table for table in tables if table.get("type") == "TOTAL"), None)
    return (overall or (tables[0] if tables else {})).get("table", [])

def get_team(code: str, team_id: int):
    if code not in LEAGUES:
        raise HTTPException(404, "Championship not found")
    if settings.mock_football_api:
        team = next((x for x in MOCK_TEAMS.get(code, []) if x[0] == team_id), None)
        if not team:
            raise HTTPException(404, "Team not found")
        return {"id": team[0], "name": team[1], "crest": "", "venue": "Football QA Stadium", "website": None}
    return _fetch(f"/teams/{team_id}")

def get_matches(code: str):
    if code not in LEAGUES:
        raise HTTPException(404, "Championship not found")
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
