from app.infraestructure.logging.LogPanelMQTT import LogPanelMQTT
from app.application.objeto_service import ObjetoService
from app.infraestructure.persistence import Persistence

def get_objeto_service():
    log_panel = LogPanelMQTT()
    persistence = Persistence()
    return ObjetoService(log_panel, persistence)
