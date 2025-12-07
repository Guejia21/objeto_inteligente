"""Archivo de configuracion global de la aplicacion."""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """Clase de configuracion global de la aplicacion."""
    ONTOLOGY_SERVICE_URL: str = os.getenv("ONTOLOGY_SERVICE_URL", "http://localhost:8001")
    OBJECT_SERVICE_URL: str = os.getenv("OBJECT_SERVICE_URL", "http://localhost:8002")
    DATASTREAMS_SERVICE_URL: str = os.getenv("DATASTREAMS_SERVICE_URL", "http://localhost:8003")
    model_config = ConfigDict(        
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

config = Settings()