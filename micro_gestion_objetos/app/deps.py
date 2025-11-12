from infraestructure.logging.LogPanelMQTT import LogPanelMQTT
from application.objeto_service import ObjetoService
from infraestructure.persistence import Persistence

def get_objeto_service():
    log_panel = LogPanelMQTT()
    persistence = Persistence()
    return ObjetoService(log_panel, persistence)
