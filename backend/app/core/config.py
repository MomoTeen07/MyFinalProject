from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://football:football@db:5432/footballqa"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    football_api_base_url: str = "https://api.football-data.org/v4"
    football_api_token: str = ""
    cors_origins: str = "http://localhost:5174"
    mock_football_api: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
