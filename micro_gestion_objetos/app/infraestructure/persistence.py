
from app.infraestructure.IRepository import IRepository
from app.infraestructure.logging.Logging import logger
import json
import os
from pathlib import Path
from app.config import settings

class Persistence(IRepository):
    def save_object_metadata(self, metadata: dict):                
        try:            
            # Asegurar que el directorio destino exista
            metadata_path = Path(settings.METADATA_PATH)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, "w", encoding="utf-8") as file:
                json.dump(metadata, file, ensure_ascii=False, indent=2)
            logger.info("Metadatos del objeto guardados correctamente.")
        except Exception as e:
            logger.error("Error al guardar los metadatos del objeto: %s", e)
            raise

    def get_object_metadata(self) -> dict:        
        try:
            with open(settings.METADATA_PATH, "r", encoding="utf-8") as file:
                metadata = json.load(file)
            logger.info("Metadatos del objeto obtenidos correctamente.")
            return metadata
        except Exception as e:
            logger.error("Error al obtener los metadatos del objeto: %s", e)
            raise
    def is_object_metadata_exists(self) -> bool:
        try:
            return Path(settings.METADATA_PATH).exists()
        except FileNotFoundError:
            logger.warning("El archivo de metadatos no existe.")
            return False
        except Exception as e:
            logger.error("Error al verificar la existencia de los metadatos del objeto: %s", e)
            raise