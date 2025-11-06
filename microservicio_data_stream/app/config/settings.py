# app/config/settings.py (Pydantic v2)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "recursos-datastreams"
    APP_VERSION: str = "1.0.0"
    OSID: str = "2"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()