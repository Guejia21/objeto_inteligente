from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
        
    # URLs de microservicios dependientes
    ONTOLOGIAS_MS_URL :str = "http://localhost:8001/ontology/"
    AUTOMATIZACION_MS_URL :str = "http://localhost:8004/eca/"
    PATH_IP_COORDINADOR :str = str(Path(__file__).resolve().parent.parent / "infrastructure" / "ipCoordinador.txt")
    PATH_ECAS : str = str(Path(__file__).resolve().parent.parent / "infrastructure/")
    IP_SERVIDOR_PERFIL_USUARIO : str = "localhost"
    # Timeouts para llamadas a microservicios
    MS_TIMEOUT :int = 30
    PORT: int = 8005
    BROKER_HOST: str = "localhost"
    BROKER_PORT: int = 1883
    model_config = ConfigDict(
        env_file='.env',
        extra='ignore'
    )
        
settings = Settings()