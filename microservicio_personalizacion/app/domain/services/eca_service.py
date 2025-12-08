import requests
from config.settings import settings
from infrastructure.logging.Logging import logger

def apagar_ecas(osid:str)->bool:
    """Apaga todas las ECAs del objeto inteligente en el microservicio de automatización.

    Args:
        osid (str): OSID del objeto inteligente
    Returns:
        bool: Indica si la operación fue exitosa o no
    """
    response = requests.patch(
        f"{settings.AUTOMATIZACION_MS_URL}eca/",
        params={"osid": osid},
        timeout=30.0
    )
    if response.status_code == 200:
        return True
    else:
        logger.error(f"Error apagando ECAs: {response.text}")
        return False