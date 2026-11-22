from typing import Literal

from fastapi import APIRouter, Query

from app.services.football_service import (
    FIXTURES_MAX_DAYS,
    NEWS_MAX_DAYS,
    get_fixtures,
    get_head_to_head,
    get_match,
    get_matches,
    get_news,
    get_press,
    get_scorers,
    get_standings,
    get_team,
    leagues,
)

router = APIRouter(prefix="/api/football", tags=["football"])

MatchStatus = Literal[
    "SCHEDULED",
    "TIMED",
    "IN_PLAY",
    "PAUSED",
    "FINISHED",
    "POSTPONED",
    "CANCELLED",
    "AWARDED",
    "SUSPENDED",
]


@router.get("/leagues")
def get_leagues():
    return leagues()


@router.get("/leagues/{code}/standings")
def standings(code: str):
    return get_standings(code)


@router.get("/leagues/{code}/matches")
def matches(
    code: str,
    page: int = Query(1, ge=1, description="Page demandée (>= 1)"),
    page_size: int = Query(50, ge=1, le=100, description="Taille de page (1..100)"),
    status: MatchStatus | None = Query(None, description="Filtrer par statut"),
    team_id: int | None = Query(
        None, ge=0, description="Filtrer sur l'équipe à domicile ou à l'extérieur"
    ),
    sort: Literal["date", "date_desc"] = Query("date", description="Ordre chronologique"),
):
    return get_matches(
        code,
        page=page,
        page_size=page_size,
        status=status,
        team_id=team_id,
        sort=sort,
    )


@router.get("/leagues/{code}/scorers")
def scorers(
    code: str,
    limit: int = Query(10, ge=1, le=50, description="Nombre de joueurs renvoyés"),
    sort: Literal["goals", "assists"] = Query("goals", description="Critère de classement"),
):
    return get_scorers(code, limit=limit, sort=sort)


@router.get("/leagues/{code}/teams/{team_id}")
def team(code: str, team_id: int):
    return get_team(code, team_id)


@router.get("/news")
def news(
    days: int = Query(
        7,
        ge=1,
        le=NEWS_MAX_DAYS,
        description="Fenêtre en jours (le fournisseur refuse plus de 10 jours d'écart)",
    ),
    limit: int = Query(10, ge=1, le=20, description="Nombre de résultats renvoyés"),
):
    return get_news(days=days, limit=limit)


@router.get("/press")
def press(limit: int = Query(5, ge=1, le=10, description="Nombre de titres renvoyés")):
    """Titres de presse : renvoie toujours 200, `available: false` en cas d'échec."""
    return get_press(limit=limit)


@router.get("/fixtures")
def fixtures(
    days: int = Query(
        3,
        ge=1,
        le=FIXTURES_MAX_DAYS,
        description="Fenêtre en jours (maximum 10 chez le fournisseur)",
    ),
    limit: int = Query(4, ge=1, le=20, description="Nombre de matchs renvoyés"),
    team_id: int | None = Query(
        None, ge=0, description="Filtrer sur une équipe (domicile ou extérieur)"
    ),
):
    return get_fixtures(days=days, limit=limit, team_id=team_id)


@router.get("/matches/{match_id}")
def match_details(match_id: int):
    return get_match(match_id)


@router.get("/matches/{match_id}/head2head")
def head_to_head(
    match_id: int,
    limit: int = Query(5, ge=1, le=10, description="Nombre de confrontations"),
):
    return get_head_to_head(match_id, limit=limit)
