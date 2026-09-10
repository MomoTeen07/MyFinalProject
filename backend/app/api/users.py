from fastapi import APIRouter, Depends
from app.api.deps import current_user
from app.db.models import User
from app.schemas.user import UserResponse
router = APIRouter(prefix="/api/users", tags=["users"])
@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)): return user
