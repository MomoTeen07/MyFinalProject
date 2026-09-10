from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.db.database import get_db
from app.db.models import Favorite, User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
router = APIRouter(prefix="/api/favorites", tags=["favorites"])
@router.get("", response_model=list[FavoriteResponse])
def list_favorites(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Favorite).filter(Favorite.user_id == user.id).order_by(Favorite.created_at.desc()).all()
@router.post("", response_model=FavoriteResponse, status_code=201)
def add_favorite(data: FavoriteCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    fav = Favorite(user_id=user.id, **data.model_dump()); db.add(fav)
    try: db.commit(); db.refresh(fav); return fav
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Team already in favorites")
@router.delete("/{favorite_id}", status_code=204)
def delete_favorite(favorite_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.id == favorite_id, Favorite.user_id == user.id).first()
    if not fav: raise HTTPException(404, "Favorite not found")
    db.delete(fav); db.commit()
