
from app.infraestructure.IRepository import IRepository
from app.infraestructure.logging.Logging import logger
import json
from app import config

class Persistence(IRepository):
    def save_object_metadata(self, metadata: dict):                
        try:            
            with open(config.pathMetadata, "w") as file:
                json.dump(metadata, file)
            logger.info("Metadatos del objeto guardados correctamente.")
        except Exception as e:
            logger.error("Error al guardar los metadatos del objeto: %s", e)
            raise

    def get_object_metadata(self) -> dict:        
        try:
            with open(config.pathMetadata, "r") as file:
                metadata = json.load(file)
            logger.info("Metadatos del objeto obtenidos correctamente.")
            return metadata
        except Exception as e:
            logger.error("Error al obtener los metadatos del objeto: %s", e)
            raise
    def is_object_metadata_exists(self) -> bool:
        try:
            with open(config.pathMetadata, "r") as file:
                return True
        except FileNotFoundError:
            logger.warning("El archivo de metadatos no existe.")
            return False
        except Exception as e:
            logger.error("Error al verificar la existencia de los metadatos del objeto: %s", e)
            raise