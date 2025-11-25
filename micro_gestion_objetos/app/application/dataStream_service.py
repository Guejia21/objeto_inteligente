"""Servicio para interactuar con el microservicio de Datastreams.

Provee funciones para consumir los endpoints del microservicio de datastream:
- send_state(osid): obtiene el estado de todos los datastreams
- send_data(osid, variable_estado, tipove): obtiene el valor de un datastream
- send_service_state(): verifica si el servicio está disponible
- send_command(osid, datastream_id, comando): envía un comando a un actuador

Basado en el patrón de ontology_service.py.
"""

from config import settings
from infraestructure.logging.Logging import logger
import requests

headers = {"Content-Type": "application/json"}


def send_service_state() -> bool:
    """Verifica si el microservicio de datastream está disponible.
    
    Hace una petición al endpoint /Datastreams/health
    
    Returns:
        True si el servicio responde correctamente, False en caso contrario.
    """
    try:
        url = settings.DATASTREAM_SERVICE_URL + "/health"
        request = requests.get(url, headers=headers, timeout=5)
        if request.status_code == 200:
            logger.info("Microservicio de datastream disponible.")
            return True
        else:
            logger.error("Error al verificar estado del microservicio de datastream: %s", request.text)
            return False
    except Exception as e:
        logger.error("Error de conexión con microservicio de datastream: %s", e)
        return False


def send_state(osid: str) -> dict:
    """Obtiene el estado de todos los datastreams del objeto inteligente.
    
    Args:
        osid (str): ID del objeto inteligente
        
    Returns:
        dict: Respuesta JSON del servicio con el estado de todos los datastreams
        
    Raises:
        ValueError: Si el osid no es válido o el servicio retorna error
    """
    if not osid:
        raise ValueError("osid es requerido")
    
    try:
        url = settings.DATASTREAM_SERVICE_URL + "/SendState"
        params = {"osid": osid}
        request = requests.get(url, params=params, headers=headers, timeout=5)
        
        if request.status_code == 200:
            try:
                data = request.json()
                logger.info("SendState exitoso para osid: %s", osid)
                return data
            except ValueError as e:
                logger.error("Error parseando respuesta JSON de SendState: %s", e)
                raise ValueError("Respuesta inválida del servicio de datastream")
        else:
            logger.error("Error en SendState para osid %s: %s", osid, request.text)
            raise ValueError(f"Error en SendState: {request.text}")
    except requests.exceptions.RequestException as e:
        logger.error("Error de conexión en SendState: %s", e)
        raise ValueError(f"Error de conexión con microservicio de datastream: {e}")


def send_data(osid: str, variable_estado: str, tipove: str =1 ) -> dict:
    """Obtiene el valor actual de un datastream específico.
    
    Args:
        osid (str): ID del objeto inteligente
        variable_estado (str): ID del datastream (p.ej. 'temperatura', 'led')
        tipove (int): Tipo de variable ()
        
    Returns:
        dict: Respuesta JSON con el valor del datastream
        
    Raises:
        ValueError: Si los parámetros no son válidos o el servicio retorna error
    """
    if not osid or not variable_estado:
        raise ValueError("osid y variable_estado son requeridos")
    
    try:
        url = settings.DATASTREAM_SERVICE_URL + "/SendData"
        params = {
            "osid": osid,
            "variableEstado": variable_estado,
            "tipove": tipove
        }
        request = requests.get(url, params=params, headers=headers, timeout=5)
        
        if request.status_code == 200:
            try:
                data = request.json()
                logger.info("SendData exitoso para osid: %s, datastream: %s", osid, variable_estado)
                return data
            except ValueError as e:
                logger.error("Error parseando respuesta JSON de SendData: %s", e)
                raise ValueError("Respuesta inválida del servicio de datastream")
        else:
            logger.error("Error en SendData para osid %s, datastream %s: %s", osid, variable_estado, request.text)
            raise ValueError(f"Error en SendData: {request.text}")
    except requests.exceptions.RequestException as e:
        logger.error("Error de conexión en SendData: %s", e)
        raise ValueError(f"Error de conexión con microservicio de datastream: {e}")


def send_command(osid: str, datastream_id: str, comando: str) -> dict:
    """Envía un comando a un actuador (datastream).
    
    Args:
        osid (str): ID del objeto inteligente
        datastream_id (str): ID del datastream actuador (p.ej. 'led', 'bomba')
        comando (str): Comando a ejecutar ('on', 'off' o valor numérico)
        
    Returns:
        dict: Respuesta JSON confirmando la ejecución del comando
        
    Raises:
        ValueError: Si los parámetros no son válidos o el servicio retorna error
    """
    if not osid or not datastream_id or not comando:
        raise ValueError("osid, datastream_id y comando son requeridos")
    
    try:
        url = config.urlDataStreamService + "/SetDatastream"
        params = {
            "osid": osid,
            "idDataStream": datastream_id,
            "comando": comando
        }
        request = requests.get(url, params=params, headers=headers, timeout=5)
        
        if request.status_code == 200:
            try:
                data = request.json()
                logger.info("SendCommand exitoso para osid: %s, datastream: %s, comando: %s", 
                           osid, datastream_id, comando)
                return data
            except ValueError as e:
                logger.error("Error parseando respuesta JSON de SendCommand: %s", e)
                raise ValueError("Respuesta inválida del servicio de datastream")
        else:
            logger.error("Error en SendCommand para osid %s, datastream %s: %s", 
                        osid, datastream_id, request.text)
            raise ValueError(f"Error en SendCommand: {request.text}")
    except requests.exceptions.RequestException as e:
        logger.error("Error de conexión en SendCommand: %s", e)
        raise ValueError(f"Error de conexión con microservicio de datastream: {e}")
