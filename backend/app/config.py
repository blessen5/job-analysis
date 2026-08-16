import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        """
        Application settings loaded from environment variables using Pydantic Settings.
        """
        APP_ENV: str = "development"
        DEBUG: bool = True
        DATABASE_URL: str = "postgresql://job_user:job_password@localhost:5432/job_market_db"

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"

except ImportError:
    class Settings:  # type: ignore
        """
        Fallback Settings class using standard os.environ for minimal setups.
        """
        def __init__(self) -> None:
            self.APP_ENV: str = os.getenv("APP_ENV", "development")
            self.DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
            self.DATABASE_URL: str = os.getenv(
                "DATABASE_URL",
                "postgresql://job_user:job_password@localhost:5432/job_market_db"
            )

settings = Settings()
