"""
Configuration module for the application.
Handles environment variables and application settings for database and SMTP connections.
"""

import os


class Settings:  # pylint: disable=too-few-public-methods
    """
    Application settings and environment variable management.
    Defines default values and computed properties for database and SMTP connections.
    """

    DB_USER: str = os.getenv("POSTGRES_USER", "user")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    DB_NAME: str = os.getenv("POSTGRES_DB", "registration_db")
    DB_HOST: str = os.getenv(
        "POSTGRES_HOST", "localhost"
    )  # 'localhost' for local development
    DB_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
    EMAILS_FROM: str = "noreply@example.com"

    @property
    def database_url(self) -> str:
        """
        Constructs the PostgreSQL connection string from individual settings.
        """
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
