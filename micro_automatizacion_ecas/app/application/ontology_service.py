
from config import settings
from infra.logging.Logging import  logger
import requests

"""Servicio para interactuar con la ontología del objeto inteligente."""
headers = {"Content-Type": "application/json"}
def is_active() -> bool:
    """Verifica si la ontología ha sido creada."""
    url = settings.ONTOLOGY_SERVICE_URL + "/consultas/consultar_active"
    request = requests.get(url, headers=headers)
    if request.status_code == 200 and request.content == b'true':
        return True
    else:
        logger.error("Error al consultar el estado de la ontología: %s", request.text)        
        return False
def get_id() -> str:
    """Obtiene el ID del objeto inteligente desde la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + "/consultas/consultar_id"
    try:
        request = requests.get(url, headers=headers)
    except Exception as e:
        logger.error("Error al conectar con el servicio de ontología: %s", e)
        return None
    if request.status_code == 200:
        try:
            data = request.json()
        except ValueError:
            # La respuesta no es JSON; devolver el texto plano
            return request.text.strip()
        if isinstance(data, dict):
            id_val = data.get("id")
            if id_val is None:
                raise ValueError("Respuesta JSON no contiene 'id'.")
            return id_val
        if isinstance(data, str):
            return data
        return str(data)
    else:
        logger.error("Error al consultar el ID del objeto inteligente: %s", request.text)
        return None
def get_title() -> str:
    """Obtiene el título del objeto inteligente desde la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + "/consultas/consultar_title"
    try:
        request = requests.get(url, headers=headers)
    except Exception as e:
        logger.error("Error al conectar con el servicio de ontología: %s", e)
        return None
    if request.status_code == 200:
        try:
            data = request.json()
        except ValueError:
            # No es JSON: devolver texto plano (o cadena vacía si está vacío)
            return request.text.strip() or ""
        # Si es dict, intentar obtener la clave 'title'
        if isinstance(data, dict):
            title_val = data.get("title")
            if title_val is None:
                return ""
            return title_val
        # Si la respuesta ya es una cadena
        if isinstance(data, str):
            return data
        # Fallback: convertir a string
        return str(data)
    else:
        logger.error("Error al consultar el título del objeto inteligente: %s", request.text)
        return None
def poblate_eca(data: dict) -> bool:
    """Puebla una regla ECA en la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + "/poblacion/poblar_eca"    
    request = requests.post(url, json=data, headers=headers)
    if request.json().get("code") == 201:
        logger.info("ECA poblada con éxito.")
        return True
    logger.error("Error al poblar el ECA: %s", request.text)
    return False
def poblate_ontology(data: dict) -> bool:
    """Puebla la ontología con los datos proporcionados."""
    url = settings.ONTOLOGY_SERVICE_URL + "/poblacion/poblar_metadatos_objeto"
    # Sanitizar payload para evitar enviar valores que Pydantic no pueda parsear
    try:
        from copy import deepcopy
        payload = deepcopy(data)
        if isinstance(payload, dict) and "dicRec" in payload and isinstance(payload.get("dicRec"), list):
            for rec in payload["dicRec"]:
                # unitType: garantizar entero (0 por defecto)
                ut = rec.get("unitType", 0)
                if ut in [None, "", "None"]:
                    rec["unitType"] = 0
                else:
                    try:
                        rec["unitType"] = int(ut)
                    except Exception:
                        rec["unitType"] = 0

                # Asegurar que tags sea lista
                if "tags" in rec and rec.get("tags") is None:
                    rec["tags"] = []

                # Normalizar valores que no deben ser None
                for k in ["symbol", "label", "datapoints", "at", "current_value", "max_value", "min_value"]:
                    if k in rec and rec.get(k) is None:
                        rec[k] = ""

    except Exception as e:
        logger.warning("Error al sanitizar payload antes de poblar ontología: %s", e)
        payload = data

    logger.debug("Payload enviado a poblar_metadatos_objeto: %s", payload)
    request = requests.post(url, json=payload, headers=headers)
    if request.status_code == 201:
        logger.info("Ontología poblada con éxito.")
        return True
    logger.error("Error al poblar la ontología: %s", request.text)
    return False