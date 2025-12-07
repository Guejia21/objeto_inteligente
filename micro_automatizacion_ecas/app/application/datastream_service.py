import requests
from config import settings
from infra.logging.Logging import logger

headers = {"Content-Type": "application/json"}
def send_command(osid:str, id_datastream: str, comando: str) -> bool:
    """Envía un comando a un datastream actuador."""
    url = settings.DATASTREAM_SERVICE_URL + f"/Datastreams/SetDatastream?osid={osid}&idDataStream={id_datastream}&comando={comando}"
    try:
        request = requests.post(url, headers=headers)
    except Exception as e:
        logger.error("Error al conectar con el servicio de datastream: %s", e)
        return False
    if request.status_code == 200:
        try:
            data = request.json()
        except ValueError:
            logger.error("Respuesta no es JSON: %s", request.text)
            return False
        if data.get("status") == "success":
            return True
        else:
            logger.error("Error en la respuesta del servicio de datastream: %s", data)
            return False
    else:
        logger.error("Error al enviar comando al datastream: %s", request.text)
        return False