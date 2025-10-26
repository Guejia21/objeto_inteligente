
from app import config
from app.infraestructure.logging.Logging import  logger
import requests

"""Servicio para interactuar con la ontología del objeto inteligente."""
headers = {"Content-Type": "application/json"}
def is_active() -> bool:
    """Verifica si la ontología ha sido creada."""
    url = config.urlOntologyService + "/consultas/consultar_active"
    request = requests.get(url, headers=headers)
    if request.status_code == 200 and request.content == b'true':
        return True
    else:
        logger.error("Error al consultar el estado de la ontología: %s", request.text)        
        return False
def get_id() -> str:
    """Obtiene el ID del objeto inteligente desde la ontología."""
    url = config.urlOntologyService + "/consultar_id"
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        return request.json().get("id")
    else:
        raise ValueError("Error al consultar el ID del objeto inteligente.")
def get_title() -> str:
    """Obtiene el título del objeto inteligente desde la ontología."""
    url = config.urlOntologyService + "/consultar_title"
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        return request.json().get("title")
    else:
        raise ValueError("Error al consultar el título del objeto inteligente.")
def poblate_ontology(data: dict) -> bool:
    """Puebla la ontología con los datos proporcionados."""
    url = config.urlOntologyService + "/poblacion/poblar_metadatos_objeto"
    request = requests.post(url, json=data, headers=headers)
    if request.status_code == 201:
        logger.info("Ontología poblada con éxito.")
        return True
    logger.error("Error al poblar la ontología: %s", request.text)
    return False