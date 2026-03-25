from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    cors_origins: str = "http://localhost:3000"
    max_file_size_mb: int = 10
    git_clone_timeout_seconds: int = 30
    redis_url: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
