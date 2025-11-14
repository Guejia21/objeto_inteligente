from app.application.consultas_service import ConsultasService 
from app.application.poblacion_service import PoblacionService
from app.infraestructure.adaptadores.ConsultasOOS import ConsultasOOS
from app.infraestructure.adaptadores.PobladorOOS import PobladorOOS

def get_consultas_service() -> ConsultasService:
    # Aquí se debería instanciar y devolver el servicio con sus dependencias
    try:
        consultas_base_conocimiento = ConsultasOOS()
    except Exception as e:
        raise ValueError("Error al inicializar el servicio de consultas: " + str(e))     
    return ConsultasService(consultas_base_conocimiento)

def get_poblacion_service() -> PoblacionService:
    # Aquí se debería instanciar y devolver el servicio con sus dependencias
    poblacion_base_conocimiento = PobladorOOS()
    return PoblacionService(poblacion_base_conocimiento)