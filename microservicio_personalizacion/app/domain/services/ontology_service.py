from infrastructure.logging.Logging import logger
from fastapi import UploadFile
import requests
from config.settings import settings
from application.dtos.request_dtos import RegistroInteraccionDTO

def get_osid():
    """Consulta el OSID del objeto al microservicio de ontologias

    Returns:
        str: OSID del objeto inteligente
    """
    try:
        response = requests.get(
        f"{settings.ONTOLOGIAS_MS_URL}consultas/consultar_id",
        timeout=10.0
    )
    except requests.RequestException as e:
        logger.error(f"Error conectando al microservicio de ontologías: {e}")
        return ""
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error consultando OSID del usuario: {response.text}")
        return ""
def cargar_ontologia(file: UploadFile, nombre: str, ipCoordinador: str) -> bool:
    """Envia la ontologia del usuario al microservicio de ontologías.

    Args:
        file (UploadFile): Archivo de ontología (.owl)
        nombre (str): Nombre de la ontología
        ipCoordinador (str): Dirección IP del coordinador

    Returns:
        bool: Indica si la carga fue exitosa o no
    """
    files = {
        "file": (file.filename, file.file, file.content_type)
    }
    data = {
        "nombre": nombre,
        "ipCoordinador": ipCoordinador
    }
    try:
        response = requests.post(
            f"{settings.ONTOLOGIAS_MS_URL}poblacion_usuario/cargar_ontologia",
            files=files,
            data=data,
            timeout=30.0
        )
    except requests.RequestException as e:
        logger.error(f"Error conectando al microservicio de ontologías: {e}")
        return False    
    if response.status_code == 201:
        return True
    else:
        logger.error(f"Error cargando ontología: {response.text}")
        return False
def consultar_email_usuario():
    """Consulta el email del usuario al microservicio de ontologias

    Returns:
        str: Email del usuario
    """
    try:
        response = requests.get(
            f"{settings.ONTOLOGIAS_MS_URL}consultas_usuario/consultar_email_usuario",
            timeout=10.0
        )
    except requests.RequestException as e:
        logger.error(f"Error conectando al microservicio de ontologías: {e}")
        return ""
    if response.status_code == 200:
        return response.json().get("email", "")
    else:
        logger.error(f"Error consultando email del usuario: {response.text}")
        return ""
def consultar_lista_preferencias_por_osid(osid:str):
    """Consulta la lista de preferencias del usuario al microservicio de ontologias

    Args:
        osid (str): OSID del objeto inteligente

    Returns:
        list: Lista de preferencias del usuario
    """
    try:
        response = requests.get(
            f"{settings.ONTOLOGIAS_MS_URL}consultas_usuario/consultar_lista_preferencias/{osid}",
            timeout=10.0
        )
    except requests.RequestException as e:
        logger.error(f"Error conectando al microservicio de ontologías: {e}")
        return []
    if response.status_code == 200:
        return response.json().get("preferencias", [])
    else:
        logger.error(f"Error consultando lista de preferencias del usuario: {response.text}")
        return []
def eliminar_ontologia_usuario()->bool:
    """Elimina la ontología del perfil de usuario en el microservicio de ontologías.

    Returns:
        bool: Indica si la eliminación fue exitosa o no
    """
    try:
        response = requests.delete(
            f"{settings.ONTOLOGIAS_MS_URL}poblacion_usuario/eliminar_ontologia_usuario",
            timeout=10.0
        )
    except requests.RequestException as e:
        logger.error(f"Error conectando al microservicio de ontologías: {e}")
        return False
    if response.status_code == 200:
        return True
    else:
        logger.error(f"Error eliminando ontología de usuario: {response.text}")
        return False
def verificar_perfil_activo()->bool:
    """Verifica si el perfil de usuario está activo en el microservicio de ontologías.

    Returns:
        bool: Indica si el perfil está activo o no
    """
    try:
        response = requests.get(
            f"{settings.ONTOLOGIAS_MS_URL}consultas_usuario/consultar_active",
            timeout=10.0
        )
    except requests.RequestException as e:
        logger.error(f"Error conectando al microservicio de ontologías: {e}")
        return False
    if response.status_code == 200:
        return response.json().get("active", False)
    else:
        logger.error(f"Error verificando estado del perfil de usuario: {response.text}")
        return False
def registrar_interaccion(data:RegistroInteraccionDTO)->bool:
    """Registra una interacción del usuario en el microservicio de ontologías.

    Args:
        data (RegistroInteraccionDTO): Datos de la interacción a registrar
    Returns:
        bool: Indica si el registro fue exitoso o no
    """
    payload = {
        "mac": data.mac,
        "email": data.email,
        "idDataStream": data.idDataStream,
        "idUsuario": data.idUsuario,
        "accion": data.accion,
        "comando": data.comando,
        "osid": data.osid,
        "dateInteraction": data.dateInteraction
    }
    try:
        response = requests.post(
            f"{settings.ONTOLOGIAS_MS_URL}poblacion_usuario/registro_interaccion",
            json=payload,
            timeout=10.0
        )
    except requests.RequestException as e:
        logger.error(f"Error conectando al microservicio de ontologías: {e}")
        return False
    if response.status_code == 200:
        return True
    else:
        logger.error(f"Error registrando interacción del usuario: {response.text}")
        return False