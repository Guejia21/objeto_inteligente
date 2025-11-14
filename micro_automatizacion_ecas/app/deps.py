from app.infra.gestion_conocimiento_client import GestionConocimientoClient 
from app.application.automatizacion_service import AutomatizacionECAService

 
def get_gestion_conocimiento_client() -> GestionConocimientoClient: 
    return GestionConocimientoClient() 
def get_automatizacion_service() -> AutomatizacionECAService: 
    client = get_gestion_conocimiento_client() 
    return AutomatizacionECAService(client=client)