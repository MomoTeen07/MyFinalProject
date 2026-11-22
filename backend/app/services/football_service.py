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
# Jeu simulé des buteurs : couvre volontairement trois cas limites utilisés par
# les tests — égalité de buts départagée par les matchs joués, égalité parfaite
# départagée par le nom, et `assists` absent (None) qui doit devenir 0.
def _scorer(player_id, name, team_id, team_name, goals, assists, penalties, played):
    return {
        "player": {"id": player_id, "name": name},
        "team": {"id": team_id, "name": team_name},
        "goals": goals,
        "assists": assists,
        "penalties": penalties,
        "playedMatches": played,
    }


MOCK_SCORERS = {
    "PL": [
        _scorer(9001, "Erling Haaland", 65, "Manchester City", 9, None, 1, 11),
        _scorer(9002, "Alexander Isak", 64, "Liverpool", 7, 2, 0, 10),
        _scorer(9003, "Bukayo Saka", 57, "Arsenal", 6, 4, 1, 9),
        _scorer(9004, "Thierno Barry", 61, "Chelsea", 6, 1, 0, 10),
        _scorer(9005, "Cole Palmer", 61, "Chelsea", 5, 5, 2, 11),
        _scorer(9006, "Kai Havertz", 57, "Arsenal", 4, None, 0, 8),
    ],
    "FL1": [
        _scorer(9101, "Mason Greenwood", 522, "Olympique de Marseille", 8, 3, 1, 11),
        _scorer(9102, "Ousmane Dembélé", 524, "Paris Saint-Germain", 7, None, 0, 9),
        _scorer(9103, "Bradley Barcola", 524, "Paris Saint-Germain", 6, 4, 0, 10),
        _scorer(9104, "Alexandre Lacazette", 516, "Olympique Lyonnais", 6, 2, 2, 11),
        _scorer(9105, "Folarin Balogun", 548, "AS Monaco", 5, 1, 0, 8),
        _scorer(9106, "Rayan Cherki", 516, "Olympique Lyonnais", 3, 6, 0, 10),
    ],
    "PD": [
        _scorer(9201, "Kylian Mbappé", 86, "Real Madrid", 10, 2, 2, 11),
        _scorer(9202, "Robert Lewandowski", 81, "Barcelona", 8, 1, 1, 9),
        _scorer(9203, "Lamine Yamal", 81, "Barcelona", 6, 7, 0, 10),
        _scorer(9204, "Antoine Griezmann", 78, "Atlético de Madrid", 6, 3, 2, 11),
        _scorer(9205, "Vinícius Júnior", 86, "Real Madrid", 5, None, 0, 8),
        _scorer(9206, "Álvaro Morata", 78, "Atlético de Madrid", 4, 2, 0, 10),
    ],
    "SA": [
        _scorer(9301, "Lautaro Martínez", 108, "Inter Milan", 9, 2, 1, 10),
        _scorer(9302, "Dušan Vlahović", 100, "Juventus", 7, None, 2, 9),
        _scorer(9303, "Rafael Leão", 98, "AC Milan", 6, 4, 0, 11),
        _scorer(9304, "Ademola Lookman", 102, "Atalanta", 6, 2, 0, 10),
        _scorer(9305, "Marcus Thuram", 108, "Inter Milan", 5, 3, 0, 9),
        _scorer(9306, "Christian Pulisic", 98, "AC Milan", 4, 5, 1, 11),
    ],
    "BL1": [
        _scorer(9401, "Harry Kane", 5, "Bayern München", 12, 3, 2, 10),
        _scorer(9402, "Serhou Guirassy", 4, "Borussia Dortmund", 8, 1, 1, 9),
        _scorer(9403, "Florian Wirtz", 3, "Bayer Leverkusen", 6, 6, 0, 11),
        _scorer(9404, "Jamal Musiala", 5, "Bayern München", 6, 4, 0, 9),
        _scorer(9405, "Robert Glatzel", 18, "Hamburger SV", 5, None, 1, 10),
        _scorer(9406, "Julian Brandt", 4, "Borussia Dortmund", 3, 5, 0, 11),
    ],
    "CL": [
        _scorer(9501, "Erling Haaland", 5, "Bayern München", 5, None, 1, 4),
        _scorer(9502, "Kylian Mbappé", 86, "Real Madrid", 5, 2, 0, 4),
        _scorer(9503, "Raphinha", 81, "FC Barcelona", 4, 3, 0, 3),
        _scorer(9504, "Mohamed Salah", 64, "Liverpool", 4, 1, 0, 4),
        _scorer(9505, "Vinícius Júnior", 86, "Real Madrid", 3, 4, 0, 4),
        _scorer(9506, "Robert Lewandowski", 81, "FC Barcelona", 2, None, 0, 4),
    ],
}

MOCK_SCORER_SEASON = {
    "startDate": "2026-08-01",
    "endDate": "2027-05-31",
    "currentMatchday": 12,
}

# Le plan gratuit du fournisseur refuse une plage `dateFrom`/`dateTo` de plus de
# 10 jours d'écart (HTTP 400 vérifié le 22/11/2026 : 11 jours passent, 12
# échouent). La borne applicative est fixée à 10 pour garder une marge.
NEWS_MAX_DAYS = 10

# Jeu simulé des actualités : couvre les trois branches de formulation
# (victoire à domicile, victoire à l'extérieur, match nul).
MOCK_NEWS = [
    ("PL", 0, 1, 2, 1, 1),
    ("PD", 2, 3, 0, 3, 2),
    ("SA", 0, 2, 1, 1, 3),
    ("FL1", 1, 3, 3, 0, 4),
    ("BL1", 0, 2, 0, 2, 5),
]

# Le fournisseur ne trie que par buts. Pour classer par passes sans rater un
# passeur peu buteur, on récupère un vivier large puis on trie côté application.
SCORER_CANDIDATE_LIMIT = 100

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


def _as_count(value) -> int:
    """Normalise un compteur du fournisseur : ``None`` et valeurs non entières → 0."""
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _normalise_scorer(entry: dict) -> dict:
    player = entry.get("player") or {}
    team = entry.get("team") or {}
    return {
        "player": {
            "id": player.get("id"),
            "name": player.get("name") or "Joueur inconnu",
        },
        "team": {
            "id": team.get("id"),
            "name": team.get("name") or "Équipe inconnue",
            "crest": team.get("crest") or "",
        },
        "goals": _as_count(entry.get("goals")),
        "assists": _as_count(entry.get("assists")),
        "penalties": _as_count(entry.get("penalties")),
        "playedMatches": _as_count(entry.get("playedMatches")),
    }


def _scorer_rank_key(scorer: dict, sort: str):
    """Clé de tri déterministe : métrique, puis buts, puis matchs, puis nom."""
    primary = scorer["goals"] if sort == "goals" else scorer["assists"]
    return (
        -primary,
        -scorer["goals"],
        scorer["playedMatches"],
        scorer["player"]["name"].casefold(),
    )


def get_scorers(code: str, limit: int = 10, sort: str = "goals"):
    if code not in LEAGUES:
        raise HTTPException(status_code=404, detail="Championship not found")

    if settings.mock_football_api:
        raw_scorers = MOCK_SCORERS[code]
        season = MOCK_SCORER_SEASON
    else:
        payload = _fetch(f"/competitions/{code}/scorers?limit={SCORER_CANDIDATE_LIMIT}")
        raw_scorers = payload.get("scorers") or []
        season = payload.get("season") or {}

    ranked = sorted(
        (_normalise_scorer(entry) for entry in raw_scorers),
        key=lambda scorer: _scorer_rank_key(scorer, sort),
    )[:limit]

    items = [
        {"position": index + 1, **scorer} for index, scorer in enumerate(ranked)
    ]

    return {
        "competition": {"code": code, **LEAGUES[code]},
        "season": {
            "startDate": season.get("startDate"),
            "endDate": season.get("endDate"),
            "currentMatchday": season.get("currentMatchday"),
        },
        "sort": sort,
        "items": items,
    }


def _headline(home_name: str, away_name: str, home_goals: int, away_goals: int) -> str:
    """Formule française stable : trois branches testables."""
    if home_goals > away_goals:
        return f"{home_name} s'impose {home_goals}-{away_goals} face à {away_name}"
    if away_goals > home_goals:
        return f"{away_name} s'impose {away_goals}-{home_goals} sur le terrain de {home_name}"
    return f"{home_name} et {away_name} se quittent dos à dos ({home_goals}-{away_goals})"


def _parse_match_date(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _mock_news_matches(from_date, to_date):
    now = datetime.now(timezone.utc)
    matches = []
    for index, (code, home_index, away_index, home_goals, away_goals, days_ago) in enumerate(
        MOCK_NEWS
    ):
        teams = MOCK_TEAMS[code]
        home_id, home_name = teams[home_index % len(teams)]
        away_id, away_name = teams[away_index % len(teams)]
        matches.append(
            {
                "id": 8000 + index,
                "utcDate": (now - timedelta(days=days_ago)).isoformat(),
                "status": "FINISHED",
                "competition": {"code": code},
                "homeTeam": {"id": home_id, "name": home_name},
                "awayTeam": {"id": away_id, "name": away_name},
                "score": {"fullTime": {"home": home_goals, "away": away_goals}},
            }
        )
    return matches


def get_news(days: int = 7, limit: int = 10):
    """Fil de résultats récents : matchs terminés des 6 championnats supportés."""
    today = datetime.now(timezone.utc).date()
    from_date = today - timedelta(days=days - 1)

    if settings.mock_football_api:
        raw_matches = _mock_news_matches(from_date, today)
    else:
        payload = _fetch(
            f"/matches?dateFrom={from_date.isoformat()}&dateTo={today.isoformat()}"
        )
        raw_matches = payload.get("matches") or []

    items = []
    for match in raw_matches:
        if match.get("status") != "FINISHED":
            continue
        code = (match.get("competition") or {}).get("code")
        if code not in LEAGUES:
            continue
        match_date = _parse_match_date(match.get("utcDate"))
        if match_date is None or not from_date <= match_date <= today:
            continue
        score = (match.get("score") or {}).get("fullTime") or {}
        home_goals, away_goals = score.get("home"), score.get("away")
        if not isinstance(home_goals, int) or not isinstance(away_goals, int):
            continue
        home_team = match.get("homeTeam") or {}
        away_team = match.get("awayTeam") or {}
        home_name = home_team.get("name") or "Équipe inconnue"
        away_name = away_team.get("name") or "Équipe inconnue"
        items.append(
            {
                "id": match.get("id"),
                "competition": {"code": code, "name": LEAGUES[code]["name"]},
                "utcDate": match.get("utcDate"),
                "status": "FINISHED",
                "homeTeam": {"id": home_team.get("id"), "name": home_name},
                "awayTeam": {"id": away_team.get("id"), "name": away_name},
                "score": {"home": home_goals, "away": away_goals},
                "headline": _headline(home_name, away_name, home_goals, away_goals),
            }
        )

    items.sort(
        key=lambda item: (item.get("utcDate") or "", item.get("id") or 0), reverse=True
    )

    return {
        "window": {"from": from_date.isoformat(), "to": today.isoformat(), "days": days},
        "items": items[:limit],
    }
