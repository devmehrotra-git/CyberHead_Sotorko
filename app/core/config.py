"""Basic application configuration."""

from pydantic import BaseModel


class Settings(BaseModel):
    """Static defaults for the initial application scaffold."""

    app_name: str = "Sotorko"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"


settings = Settings()
