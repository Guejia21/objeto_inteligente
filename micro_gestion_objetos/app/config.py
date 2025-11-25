"""Archivo de configuración para la aplicación."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path

class Settings(BaseSettings):
    BASE_URL: str = 'http://localhost:8002'    
    RABBIT_URL: str = "amqp://guest:guest@localhost:5672/"
    REGISTER_DATASTREAMS_QUEUE_NAME: str = 'register_datastreams_queue'
    ONTOLOGY_SERVICE_URL: str = "http://localhost:8001/ontology"    
    DATASTREAM_SERVICE_URL: str = "http://localhost:8003/Datastreams"
    METADATA_PATH:str = str(Path(__file__).resolve().parent / "infraestructure" / "metadata" / "metadata.json")
    BROKER_HOST: str = "localhost"
    PORT: int = 8002
    model_config = ConfigDict(
        env_file='.env',
        extra='ignore'
    )


settings = Settings()
