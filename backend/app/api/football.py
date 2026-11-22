from typing import Literal

from fastapi import APIRouter, Query

from app.services.football_service import (
    NEWS_MAX_DAYS,
    get_matches,
    get_news,
    get_press,
    get_scorers,
    get_standings,
    get_team,
    leagues,
)

router = APIRouter(prefix="/api/football", tags=["football"])


@router.get("/leagues")
def get_leagues():
    return leagues()


@router.get("/leagues/{code}/standings")
def standings(code: str):
    return get_standings(code)


@router.get("/leagues/{code}/matches")
def matches(code: str):
    return get_matches(code)


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
