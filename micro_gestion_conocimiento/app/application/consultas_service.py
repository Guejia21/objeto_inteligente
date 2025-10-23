from app.infraestructure.interfaces.IConsultas import IConsultasOOS

class ConsultasService:
    """Servicio de Consultas para la Ontología OOS."""
    def __init__(self, gestion_base_conocimiento: IConsultasOOS):
        self.gestion_base_conocimiento = gestion_base_conocimiento
    def consultar_id(self) -> str:
        """Retorna el ID del objeto inteligente desde la base de conocimiento."""        
        return self.gestion_base_conocimiento.consultarId()
    def consultar_description(self) -> str:
        """Retorna la descripción del estado desde la base de conocimiento."""
        return self.gestion_base_conocimiento.consultarDescription()
    