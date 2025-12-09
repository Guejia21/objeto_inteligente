
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
    """Puebla una nueva regla ECA en la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + "/poblacion/poblar_eca"    
    request = requests.post(url, json=data, headers=headers)
    if request.status_code == 201:
        logger.info("ECA poblada con éxito.")
        return True
    logger.error("Error al poblar el ECA: %s", request.text)
    return False
def edit_eca(data: dict) -> bool:
    """Edita una regla ECA en la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + "/poblacion/editar_eca"    
    request = requests.post(url, json=data, headers=headers)
    if request.status_code == 200:
        logger.info("ECA editada con éxito.")
        return True
    logger.error("Error al editar el ECA: %s", request.text)
    return False
def get_ecas()-> list:
    """Obtiene todas las reglas ECA desde la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + "/consultas/listar_ecas"
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        try:
            data = request.json()
            return data
        except ValueError:
            logger.error("Respuesta no es JSON: %s", request.text)
            return None
    else:
        logger.error("Error al consultar las ECAs: %s", request.text)
        return None
def listarDinamicEstado(estado: str) -> list:
    """Lista las ECAs por estado (on/off)"""
    url = settings.ONTOLOGY_SERVICE_URL + f"/consultas/listar_dinamic_estado?eca_state={estado}"
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        try:
            data = request.json()
            return data
        except ValueError:
            logger.error("Respuesta no es JSON: %s", request.text)
            return None
    else:
        logger.error("Error al consultar las ECAs por estado: %s", request.text)
        return None
def setEcaListState(lista_ecas: list) -> bool:
    """Actualiza el estado de una lista de ECAs."""
    url = settings.ONTOLOGY_SERVICE_URL + "/consultas/set_eca_list_state"
    payload = {"ecas": lista_ecas}
    request = requests.patch(url, json=payload, headers=headers)
    if request.status_code == 200:
        logger.info("Estados de ECAs actualizados con éxito.")
        return True
    logger.error("Error al actualizar los estados de las ECAs: %s", request.text)
    return False
def delete_eca(eca_name: str) -> bool:
    """Elimina una regla ECA de la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + f"/consultas/eliminar_eca?nombreECA={eca_name}"
    request = requests.delete(url, headers=headers)
    if request.status_code == 200:
        logger.info("ECA eliminada con éxito.")
        return True
    logger.error("Error al eliminar el ECA: %s", request.text)
    return False
def set_eca_state(eca_name: str, new_state: str) -> bool:
    """Actualiza el estado de una regla ECA en la ontología."""
    url = settings.ONTOLOGY_SERVICE_URL + "/consultas/set_eca_state?valorNuevo=" + new_state + "&nombreECA=" + eca_name
    request = requests.patch(url, headers=headers)
    if request.status_code == 200:
        logger.info("Estado de ECA actualizado con éxito.")
        return True
    logger.error("Error al actualizar el estado de la ECA: %s", request.text)
    return False
def verificar_contrato(osid:str,osidDestino:str)-> list:
    """Verifica si existe un contrato ECA entre dos objetos inteligentes.

    Args:
        osid (str): Id del objeto inteligente que envía la acción.
        osidDestino (str): Id del objeto inteligente que recibe la acción.
    Returns:
        list: Lista de contratos ECA entre los dos objetos inteligentes.
    """
    url = settings.ONTOLOGY_SERVICE_URL + f"/consultas/verificar_contrato/{osid}/{osidDestino}"
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        try:
            data = request.json()
            return data
        except ValueError:
            logger.error("Respuesta no es JSON: %s", request.text)
            return None
    else:
        logger.error("Error al verificar el contrato ECA: %s", request.text)
        return None
