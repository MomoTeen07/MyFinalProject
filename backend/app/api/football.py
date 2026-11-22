from typing import Literal

from fastapi import APIRouter, Query

from app.services.football_service import (
    get_matches,
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
