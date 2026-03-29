import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./official_sim.db"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    service_name: str = "official-sim-server"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    db_echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
