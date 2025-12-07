from application.eca_service import EcaService
from infra.logging.LogPanelMQTT import LogPanelMQTT
import os
from config import settings
from infra.logging.Logging import logger
from domain.eca import ECA
from domain.eca_task_manager import eca_task_manager

def get_eca_service() -> EcaService: 
    log = LogPanelMQTT()
    return EcaService(log_panel=log)
async def load_ecas_on_startup():
    eca_path = settings.PATH_ECA
    if not os.path.exists(eca_path):
        logger.info(f"No existe el directorio de ECAs en {eca_path}. No se cargarán ECAs al iniciar.")
        return
    eca = ECA()
    logger.info(f"Cargando ECAs desde {eca_path}...")
    for filename in os.listdir(eca_path):
        if filename.endswith(".json"):
            diccionario_eca = eca.getDiccionarioECA(filename)
            if diccionario_eca:
                success = await eca_task_manager.register_eca(diccionario_eca)
                if success:
                    logger.info(f"ECA cargada al iniciar: {filename}")
                else:
                    logger.error(f"No se pudo registrar la ECA al iniciar: {filename}")
            else:
                logger.error(f"No se pudo obtener el diccionario de la ECA desde el archivo: {filename}")
def get_broker():
    log = LogPanelMQTT()
    return log