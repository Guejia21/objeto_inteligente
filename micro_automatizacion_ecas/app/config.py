"""Archivo de configuración para la aplicación."""
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    BASE_URL: str = 'http://localhost:8004'        
    ONTOLOGY_SERVICE_URL: str = "http://localhost:8001/ontology"    
    DATASTREAM_SERVICE_URL: str = "http://localhost:8003/Datastreams"
    BROKER_HOST: str = "localhost"
    BROKER_PORT: int = 1883
    HTTP_TIMEOUT: float = 10.0    
    PATH_ECA: str = str(Path(__file__).resolve().parent / "infra" / "ECA") #Carpeta donde se guardan las ECAs
    PATH_COMANDOS: str = str(Path(__file__).resolve().parent / "infra" / "Comandos/") #Carpeta donde se guardan los comandos
    PORT: int = 8004
    MQTT_TELEMETRY_TOPIC: str = "datastream/telemetry"
    model_config = ConfigDict(
        env_file='.env',
        extra='ignore'
    )


settings = Settings()
