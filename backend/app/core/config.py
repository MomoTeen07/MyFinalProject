from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
ENV_FILE = PROJECT_ENV_FILE if PROJECT_ENV_FILE.is_file() else ".env"

class Settings(BaseSettings):
    database_url: str = Field(min_length=1)
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    football_api_base_url: str = "https://api.football-data.org/v4"
    football_api_token: str = ""
    football_cache_ttl_seconds: int = Field(default=300, ge=0, le=3600)
    cors_origins: str = "http://localhost:5174"
    mock_football_api: bool = False
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @field_validator("jwt_secret")
    @classmethod
    def reject_placeholder_secrets(cls, value: str) -> str:
        if value.lower().startswith(("replace-with", "change-me", "your-secret")):
            raise ValueError("JWT_SECRET must be changed from the example placeholder")
        return value

settings = Settings()
