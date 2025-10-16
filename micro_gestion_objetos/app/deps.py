from app.infraestructure.logging.LogPanelMQTT import LogPanelMQTT
from application import ObjetoService

def get_objeto_service():
    log_panel = LogPanelMQTT()
    return ObjetoService(log_panel)
