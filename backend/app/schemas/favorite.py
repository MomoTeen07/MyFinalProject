from datetime import datetime
from pydantic import BaseModel
class FavoriteCreate(BaseModel):
    team_id: int
    team_name: str
    team_crest: str | None = None
class FavoriteResponse(FavoriteCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}
