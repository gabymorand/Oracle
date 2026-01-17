from pydantic_settings import BaseSettings


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
        env_file = ".env"
        case_sensitive = False


settings = Settings()
