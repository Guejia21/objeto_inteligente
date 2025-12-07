"""Este archivo contiene la configuración de la aplicación (Rutas,)."""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

BASE_PATH = os.getcwd()

class Settings(BaseSettings):
    BASE_URL: str = 'http://localhost:8001'    
    RABBIT_URL: str = "amqp://guest:guest@localhost:5672/"        
    PORT: int = 8001
    PATH_OWL: str = BASE_PATH + '/infraestructure/OWL/'
    ONTOLOGIA: str = PATH_OWL+'ontologiav18.owl'
    ONTOLOGIA_PU: str = PATH_OWL+'ontologiaPU.owl'
    ONTOLOGIA_INSTANCIADA: str = PATH_OWL+'ontologiaInstanciada.owl'
    model_config = ConfigDict(
        env_file='.env',
        extra='ignore'
    )


settings = Settings()