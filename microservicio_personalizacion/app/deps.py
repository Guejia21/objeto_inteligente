from domain.services.personalizacion_service import PersonalizacionService
from infrastructure.logging.LogPanelMQTT import LogPanelMQTT

def get_personalizacion_service() -> PersonalizacionService:
    """Inyección de dependencia para PersonalizacionService"""   
    log = LogPanelMQTT()     
    return PersonalizacionService(log=log)