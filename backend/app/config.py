from pathlib import Path

from pydantic_settings import BaseSettings

# Find .env file - try both backend/.env and project root .env
_backend_dir = Path(__file__).parent.parent
_env_file = _backend_dir / ".env"
if not _env_file.exists():
    _env_file = _backend_dir.parent / ".env"


class Settings(BaseSettings):
    database_url: str
    riot_api_key: str
    riot_api_region: str = "euw1"
    riot_api_cache_ttl: int = 3600
    access_code: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 720  # 30 days

    class Config:
        env_file = str(_env_file)
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars like VITE_*, POSTGRES_*


settings = Settings()
