from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.database import get_db
from app.db.models import Favorite, User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.services.football_service import get_favorites_overview

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteResponse])
def list_favorites(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


@router.get("/overview")
def favorites_overview(
    user: User = Depends(current_user), db: Session = Depends(get_db)
):
    """Tableau de bord : classement, derniers résultats et prochain match."""
    favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return get_favorites_overview(
        [
            {
                "id": favorite.id,
                "team_id": favorite.team_id,
                "league_code": favorite.league_code,
                "team_name": favorite.team_name,
                "team_crest": favorite.team_crest,
            }
            for favorite in favorites
        ]
    )


@router.post("", response_model=FavoriteResponse, status_code=201)
def add_favorite(
    data: FavoriteCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    favorite = Favorite(user_id=user.id, **data.model_dump())
    db.add(favorite)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Team already in favorites") from exc
    db.refresh(favorite)
    return favorite


@router.delete("/{favorite_id}", status_code=204)
def delete_favorite(
    favorite_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    favorite = (
        db.query(Favorite)
        .filter(Favorite.id == favorite_id, Favorite.user_id == user.id)
        .first()
    )
    if favorite is None:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
