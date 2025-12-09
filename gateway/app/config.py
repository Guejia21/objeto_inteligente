"""Archivo de configuracion global de la aplicacion."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """Clase de configuracion global de la aplicacion."""
    OBJECT_SERVICE_URL :str = "http://localhost:8002"
    DATASTREAMS_SERVICE_URL : str = "http://localhost:8003"
    ONTOLOGY_SERVICE_URL : str = "http://localhost:8001"
    ECA_SERVICE_URL : str = "http://localhost:8004"
    PERSONALIZACION_SERVICE_URL : str = "http://localhost:8005"
    PORT: int = 8000
    model_config = ConfigDict(        
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

config = Settings()