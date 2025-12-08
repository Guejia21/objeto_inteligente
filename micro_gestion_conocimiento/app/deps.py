from application.consultas_service import ConsultasOntologiaUsuarioService, ConsultasService 
from application.poblacion_service import PoblacionOntologiaUsuarioService, PoblacionService
from infraestructure.adaptadores.ConsultasOOS import ConsultasOOS
from infraestructure.adaptadores.PobladorOOS import PobladorOOS
from infraestructure.adaptadores.ConsultasPerfilUsuario import ConsultasPerfilUsuario


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
    
def get_consultas_pu_service()-> ConsultasOntologiaUsuarioService:
    consultas_base_conocimiento = ConsultasPerfilUsuario()
    return ConsultasOntologiaUsuarioService(consultas_base_conocimiento)
def get_poblacion_pu_service() -> PoblacionOntologiaUsuarioService:    
    return PoblacionOntologiaUsuarioService()

