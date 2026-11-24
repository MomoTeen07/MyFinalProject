from datetime import datetime, timedelta, timezone
from copy import deepcopy
from email.utils import parsedate_to_datetime
import re
from threading import Lock
from time import monotonic
import xml.etree.ElementTree as ET

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
# Même contrainte pour toute fenêtre dateFrom/dateTo (prochains matchs, favoris).
FIXTURES_MAX_DAYS = 10
# Fenêtre du tableau de bord des favoris : les URL du fournisseur sont
# volontairement identiques à celles de `/news` (7 jours) et `/fixtures` (10
# jours) pour réutiliser le même cache et ne pas consommer de quota en plus.
FAVORITES_LOOKBACK_DAYS = 7
FAVORITES_LOOKAHEAD_DAYS = 10

# Jeu simulé des actualités : couvre les trois branches de formulation
# (victoire à domicile, victoire à l'extérieur, match nul).
MOCK_NEWS = [
    ("PL", 0, 1, 2, 1, 1),
    ("PD", 2, 3, 0, 3, 2),
    ("SA", 0, 2, 1, 1, 3),
    ("FL1", 1, 3, 3, 0, 4),
    ("BL1", 0, 2, 0, 2, 5),
]

PRESS_SOURCE_NAME = "RMC Sport"
PRESS_MAX_TITLE = 140
_HTML_TAG = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")
# (horodatage monotone, titres parsés, date de récupération ISO)
_PRESS_CACHE: tuple[float, list[dict], str] | None = None
_PRESS_LOCK = Lock()

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


def _fetch(path: str, missing_statuses: tuple[int, ...] = ()):
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
        if exc.response.status_code in missing_statuses:
            raise HTTPException(status_code=404, detail="Resource not found") from exc
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
                "form": "WWDLW",
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


# Jeu simulé des matchs : 6 rencontres par championnat, dont 2 terminées, pour
# que pagination, filtres et tri restent démontrables hors ligne.
# (décalage en jours, statut, index domicile, index extérieur, buts domicile, buts extérieur)
MOCK_MATCH_FIXTURES = (
    (-7, "FINISHED", 0, 1, 2, 1),
    (-3, "FINISHED", 2, 3, 0, 0),
    (1, "SCHEDULED", 1, 2, None, None),
    (2, "TIMED", 3, 0, None, None),
    (3, "SCHEDULED", 0, 2, None, None),
    (5, "SCHEDULED", 1, 3, None, None),
)


def _mock_matches(code: str) -> list[dict]:
    teams = MOCK_TEAMS[code]
    now = datetime.now(timezone.utc)
    matches = []
    for index, (day_offset, status, home_index, away_index, home, away) in enumerate(
        MOCK_MATCH_FIXTURES
    ):
        home_team = teams[home_index]
        away_team = teams[away_index]
        matches.append(
            {
                "id": index + 1,
                "utcDate": (now + timedelta(days=day_offset)).isoformat(),
                "status": status,
                "homeTeam": {"id": home_team[0], "name": home_team[1]},
                "awayTeam": {"id": away_team[0], "name": away_team[1]},
                "score": {"fullTime": {"home": home, "away": away}},
            }
        )
    return matches


def get_matches(
    code: str,
    page: int = 1,
    page_size: int = 50,
    status: str | None = None,
    team_id: int | None = None,
    sort: str = "date",
):
    """Calendrier paginé : filtrage et tri applicatifs, liste complète en cache."""
    if code not in LEAGUES:
        raise HTTPException(status_code=404, detail="Championship not found")

    if settings.mock_football_api:
        matches = _mock_matches(code)
    else:
        matches = _fetch(f"/competitions/{code}/matches").get("matches", [])

    if status:
        matches = [match for match in matches if match.get("status") == status]
    if team_id is not None:
        matches = [
            match
            for match in matches
            if (match.get("homeTeam") or {}).get("id") == team_id
            or (match.get("awayTeam") or {}).get("id") == team_id
        ]

    matches = sorted(
        matches,
        key=lambda match: (match.get("utcDate") or "", match.get("id") or 0),
        reverse=sort == "date_desc",
    )

    total = len(matches)
    total_pages = (total + page_size - 1) // page_size if total else 0
    start = (page - 1) * page_size
    return {
        "items": matches[start : start + page_size],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def _match_summary(match: dict, code: str | None = None) -> dict:
    """Vue minimale et stable d'un match, quel que soit l'endpoint source."""
    competition = match.get("competition") or {}
    summary_code = competition.get("code") or code
    score = (match.get("score") or {}).get("fullTime") or {}
    home = match.get("homeTeam") or {}
    away = match.get("awayTeam") or {}
    return {
        "id": match.get("id"),
        "utcDate": match.get("utcDate"),
        "status": match.get("status"),
        "competition": {
            "code": summary_code,
            "name": LEAGUES.get(summary_code, {}).get("name")
            or competition.get("name")
            or "Compétition",
        },
        "homeTeam": {
            "id": home.get("id"),
            "name": home.get("name") or "Équipe inconnue",
        },
        "awayTeam": {
            "id": away.get("id"),
            "name": away.get("name") or "Équipe inconnue",
        },
        "score": {"home": score.get("home"), "away": score.get("away")},
    }


def get_fixtures(days: int = 3, limit: int = 4, team_id: int | None = None):
    """Prochains matchs des 6 compétitions supportées, sur une fenêtre courte."""
    now = datetime.now(timezone.utc)
    today = now.date()
    to_date = today + timedelta(days=days - 1)

    if settings.mock_football_api:
        raw_matches = [
            {**match, "competition": {"code": code}}
            for code in LEAGUES
            for match in _mock_matches(code)
        ]
    else:
        payload = _fetch(
            f"/matches?dateFrom={today.isoformat()}&dateTo={to_date.isoformat()}"
        )
        raw_matches = payload.get("matches") or []

    items = []
    for match in raw_matches:
        if match.get("status") not in {"SCHEDULED", "TIMED"}:
            continue
        code = (match.get("competition") or {}).get("code")
        if code not in LEAGUES:
            continue
        if team_id is not None and team_id not in (
            (match.get("homeTeam") or {}).get("id"),
            (match.get("awayTeam") or {}).get("id"),
        ):
            continue
        match_datetime = _parse_match_datetime(match.get("utcDate"))
        if (
            match_datetime is None
            or match_datetime < now
            or match_datetime.date() > to_date
        ):
            continue
        items.append(_match_summary(match, code))

    items.sort(key=lambda item: (item.get("utcDate") or "", item.get("id") or 0))
    return {
        "window": {"from": today.isoformat(), "to": to_date.isoformat(), "days": days},
        "items": items[:limit],
    }


def get_head_to_head(match_id: int, limit: int = 5):
    """Confrontations directes autour d'un match. 404 local si le match est inconnu."""
    if settings.mock_football_api:
        if not any(match["id"] == match_id for match in _mock_matches("PL")):
            raise HTTPException(status_code=404, detail="Match not found")
        return {"match_id": match_id, "aggregates": None, "items": []}

    payload = _fetch(
        f"/matches/{match_id}/head2head?limit={limit}", missing_statuses=(400, 404)
    )
    items = [
        _match_summary(match, (match.get("competition") or {}).get("code"))
        for match in payload.get("matches") or []
    ]
    items.sort(
        key=lambda item: (item.get("utcDate") or "", item.get("id") or 0), reverse=True
    )
    return {
        "match_id": match_id,
        "aggregates": payload.get("aggregates"),
        "items": items,
    }


def _recent_and_next(matches: list[dict]):
    """Sépare les derniers résultats et le prochain match d'une liste normalisée."""
    now = datetime.now(timezone.utc)
    recent = sorted(
        (
            match
            for match in matches
            if match["status"] == "FINISHED"
            and match["score"]["home"] is not None
            and match["score"]["away"] is not None
        ),
        key=lambda match: (match.get("utcDate") or "", match.get("id") or 0),
        reverse=True,
    )[:3]
    upcoming = sorted(
        (
            match
            for match in matches
            if match["status"] in {"SCHEDULED", "TIMED"}
            and (_parse_match_datetime(match.get("utcDate")) or now) >= now
        ),
        key=lambda match: (match.get("utcDate") or "", match.get("id") or 0),
    )
    return recent, upcoming[0] if upcoming else None


def get_favorites_overview(favorites: list[dict]):
    """Tableau de bord des favoris : classement, derniers résultats, prochain match."""
    today = datetime.now(timezone.utc).date()
    past_from = today - timedelta(days=FAVORITES_LOOKBACK_DAYS - 1)
    next_to = today + timedelta(days=FAVORITES_LOOKAHEAD_DAYS - 1)

    if not favorites:
        return {
            "window": {"from": past_from.isoformat(), "to": next_to.isoformat()},
            "items": [],
        }

    if settings.mock_football_api:
        raw_matches = [
            {**match, "competition": {"code": code}}
            for code in LEAGUES
            for match in _mock_matches(code)
        ]
    else:
        raw_matches = []
        # Fenêtres partagées avec /news et /fixtures : elles couvrent les matchs
        # récents et proches, toutes compétitions confondues.
        for window_from, window_to in ((past_from, today), (today, next_to)):
            try:
                payload = _fetch(
                    f"/matches?dateFrom={window_from.isoformat()}"
                    f"&dateTo={window_to.isoformat()}"
                )
                raw_matches.extend(payload.get("matches") or [])
            except HTTPException:
                # Le tableau de bord reste utilisable même si le fournisseur
                # limite le débit : les cartes s'affichent sans contexte sportif.
                continue

    matches_by_team: dict[int, list[dict]] = {}
    for match in raw_matches:
        code = (match.get("competition") or {}).get("code")
        if code not in LEAGUES:
            continue
        summary = _match_summary(match, code)
        for team in (summary["homeTeam"], summary["awayTeam"]):
            team_id = team.get("id")
            if team_id is not None:
                matches_by_team.setdefault(team_id, []).append(summary)

    standings_by_league: dict[str, list[dict]] = {}
    fallback_matches: dict[str, list[dict]] = {}
    items = []
    for favorite in favorites:
        code = favorite.get("league_code")
        team_id = favorite.get("team_id")
        matches = matches_by_team.get(team_id, [])
        recent, next_match = _recent_and_next(matches)

        # La fenêtre courte peut manquer de résultats ou de matchs lointains :
        # le calendrier complet du championnat complète alors l'information.
        if code in LEAGUES and (len(recent) < 3 or next_match is None):
            if code not in fallback_matches:
                if settings.mock_football_api:
                    fallback_matches[code] = _mock_matches(code)
                else:
                    try:
                        payload = _fetch(f"/competitions/{code}/matches")
                        fallback_matches[code] = payload.get("matches") or []
                    except HTTPException:
                        fallback_matches[code] = []
            merged = {
                match["id"]: match
                for match in matches
                + [
                    _match_summary(match, code)
                    for match in fallback_matches[code]
                    if team_id
                    in (
                        (match.get("homeTeam") or {}).get("id"),
                        (match.get("awayTeam") or {}).get("id"),
                    )
                ]
                if match["id"] is not None
            }
            recent, next_match = _recent_and_next(list(merged.values()))

        rank = None
        if code in LEAGUES:
            if code not in standings_by_league:
                try:
                    standings_by_league[code] = get_standings(code)
                except HTTPException:
                    standings_by_league[code] = []
            row = next(
                (
                    entry
                    for entry in standings_by_league[code]
                    if (entry.get("team") or {}).get("id") == team_id
                ),
                None,
            )
            if row:
                rank = {
                    "position": row.get("position"),
                    "points": row.get("points"),
                    "playedGames": row.get("playedGames"),
                    "form": row.get("form"),
                }

        items.append(
            {
                **favorite,
                "rank": rank,
                "recent": recent,
                "next": next_match,
            }
        )

    return {
        "window": {"from": past_from.isoformat(), "to": next_to.isoformat()},
        "items": items,
    }


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


def _parse_match_datetime(value):
    """Horodatage UTC d'un match, heure comprise."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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


def _clean_press_title(value) -> str:
    """Retire les balises HTML, normalise les espaces et tronque le titre."""
    if not value:
        return ""
    text = _HTML_TAG.sub(" ", value)
    text = _WHITESPACE.sub(" ", text).strip()
    return text[:PRESS_MAX_TITLE]


def _press_published_at(value):
    """Convertit une date RFC 822 en ISO 8601 UTC ; ``None`` si illisible."""
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_press_feed(content: bytes) -> list[dict]:
    """Parse un flux RSS et ne conserve que titre, lien et date."""
    root = ET.fromstring(content)
    channel = root.find("channel")
    entries = channel.findall("item") if channel is not None else []
    items = []
    for entry in entries:
        title = _clean_press_title(entry.findtext("title"))
        link = (entry.findtext("link") or "").strip()
        if not title or not link.startswith(("http://", "https://")):
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "publishedAt": _press_published_at(entry.findtext("pubDate")),
            }
        )
    items.sort(key=lambda item: item["publishedAt"] or "", reverse=True)
    return items


def _press_items():
    """Récupère le flux presse avec cache. Toute erreur donne une liste vide."""
    global _PRESS_CACHE

    now = monotonic()
    ttl = settings.press_cache_ttl_seconds
    if ttl > 0:
        with _PRESS_LOCK:
            if _PRESS_CACHE and now - _PRESS_CACHE[0] < ttl:
                return deepcopy(_PRESS_CACHE[1]), _PRESS_CACHE[2]

    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    items: list[dict] = []
    try:
        response = httpx.get(
            settings.press_feed_url,
            timeout=settings.press_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "FootballQA/1.0 (+projet QA)"},
        )
        response.raise_for_status()
        items = _parse_press_feed(response.content)
    except Exception:  # source non contractuelle : jamais bloquante
        items = []

    if ttl > 0:
        with _PRESS_LOCK:
            _PRESS_CACHE = (monotonic(), deepcopy(items), fetched_at)

    return items, fetched_at


def get_press(limit: int = 5):
    """Bloc presse : ne renvoie jamais d'erreur, même si le flux est indisponible."""
    items, fetched_at = _press_items()
    available = bool(items)
    return {
        "available": available,
        "source": {"name": PRESS_SOURCE_NAME, "url": settings.press_feed_url},
        "fetchedAt": fetched_at,
        "items": items[:limit] if available else [],
    }


def _team_detail(team: dict) -> dict:
    """Conserve les champs enrichis quand le plan fournisseur les expose."""
    detail = {
        "id": team.get("id"),
        "name": team.get("name") or "Équipe inconnue",
        "shortName": team.get("shortName"),
        "tla": team.get("tla"),
        "crest": team.get("crest") or "",
    }
    for key in ("coach", "formation", "lineup", "bench", "statistics"):
        if key in team and team[key] is not None:
            detail[key] = team[key]
    return detail


def get_match(match_id: int):
    """Détail d'un match. Un identifiant inconnu renvoie 404, jamais 502."""
    if settings.mock_football_api:
        match = next(
            (item for item in _mock_matches("PL") if item["id"] == match_id), None
        )
        if match is None:
            raise HTTPException(status_code=404, detail="Match not found")
        score = (match.get("score") or {}).get("fullTime") or {}
        return {
            "id": match["id"],
            "competition": {"code": "PL", "name": LEAGUES["PL"]["name"]},
            "utcDate": match["utcDate"],
            "status": match["status"],
            "venue": "Football QA Stadium",
            "matchday": match["id"],
            "stage": "REGULAR_SEASON",
            "group": None,
            "homeTeam": {**match["homeTeam"], "crest": ""},
            "awayTeam": {**match["awayTeam"], "crest": ""},
            "score": {
                "home": score.get("home"),
                "away": score.get("away"),
                "halfTime": {"home": None, "away": None},
                "winner": None,
                "duration": "REGULAR",
            },
            "goals": [],
            "bookings": [],
            "substitutions": [],
            "penalties": [],
            "referees": [],
        }

    # Le fournisseur répond 400 (ou 404) pour un identifiant inconnu : la
    # nouvelle route le traduit en 404. ANO-005 reste ouverte sur /teams.
    payload = _fetch(f"/matches/{match_id}", missing_statuses=(400, 404))

    competition = payload.get("competition") or {}
    code = competition.get("code")
    score_payload = payload.get("score") or {}
    full_time = score_payload.get("fullTime") or {}
    half_time = score_payload.get("halfTime") or {}

    return {
        "id": payload.get("id", match_id),
        "competition": {
            "code": code,
            "name": LEAGUES.get(code, {}).get("name")
            or competition.get("name")
            or "Compétition",
        },
        "utcDate": payload.get("utcDate"),
        "status": payload.get("status"),
        "minute": payload.get("minute"),
        "injuryTime": payload.get("injuryTime"),
        "attendance": payload.get("attendance"),
        "venue": payload.get("venue"),
        "matchday": payload.get("matchday"),
        "stage": payload.get("stage"),
        "group": payload.get("group"),
        "lastUpdated": payload.get("lastUpdated"),
        "homeTeam": _team_detail(payload.get("homeTeam") or {}),
        "awayTeam": _team_detail(payload.get("awayTeam") or {}),
        "score": {
            "home": full_time.get("home"),
            "away": full_time.get("away"),
            "halfTime": {
                "home": half_time.get("home"),
                "away": half_time.get("away"),
            },
            "winner": score_payload.get("winner"),
            "duration": score_payload.get("duration"),
        },
        "goals": payload.get("goals") or [],
        "bookings": payload.get("bookings") or [],
        "substitutions": payload.get("substitutions") or [],
        "penalties": payload.get("penalties") or [],
        "referees": payload.get("referees") or [],
    }
