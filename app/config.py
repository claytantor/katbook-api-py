from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Server
    port: int = 8000
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/katbook"

    # Redis (optional)
    redis_url: str | None = None

    # Security
    jwt_secret: str = "change-me-in-production"
    api_key_prefix: str = "katbook_"

    # Twitter/X OAuth
    twitter_client_id: str = ""
    twitter_client_secret: str = ""

    # Rate limits
    rate_limit_general: str = "100/minute"
    rate_limit_posts: str = "1/30minutes"
    rate_limit_comments: str = "50/hour"


settings = Settings()
