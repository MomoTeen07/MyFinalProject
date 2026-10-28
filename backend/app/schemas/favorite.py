from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class FavoriteCreate(BaseModel):
    team_id: int = Field(gt=0)
    league_code: str | None = Field(default=None, min_length=2, max_length=10, pattern="^[A-Z0-9]+$")
    team_name: str = Field(min_length=1, max_length=150)
    team_crest: str | None = Field(default=None, max_length=500)

    @field_validator("team_name")
    @classmethod
    def normalize_team_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Team name cannot be empty")
        return value
class FavoriteResponse(FavoriteCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}
