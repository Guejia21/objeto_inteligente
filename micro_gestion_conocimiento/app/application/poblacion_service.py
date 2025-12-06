import os
from infraestructure.interfaces import IPoblacionPerfilUsuario
from infraestructure.interfaces.IConsultasPerfilUsuario import IConsultasPerfilUsuario
from infraestructure.interfaces.IPoblacion import IPoblacion
from infraestructure.logging.Logging import logger
import config

class PoblacionService:
    """Clase base para servicios de población."""
    
    def __init__(self, gestion_poblacion: IPoblacion):
        self.gestion_poblacion = gestion_poblacion

    def poblar_metadatos_objeto(self, diccionarioObjeto:dict, listaRecursos:dict ) -> None:
        """Pobla los metadatos del objeto inteligente en la base de conocimiento."""
        print(diccionarioObjeto)
        print(listaRecursos)
        if self.gestion_poblacion.poblarMetadatosObjeto(diccionarioObjeto, listaRecursos):
            return {"status": "Población exitosa"}
        else:
            return {"status": "Fallo en la población"}
    def poblar_eca(self, diccionarioECA:dict) -> None:
        """Pobla las reglas ECA en la base de conocimiento."""
        if self.gestion_poblacion.poblarECA(diccionarioECA):
            return {
                "code": 201,
                "status": "Población ECA exitosa"
                }
        else:
            return {
                "code": 400,
                "status": "Fallo en la población ECA"
            }
    def editar_eca(self, diccionarioECA:dict) -> None:
        """Edita un ECA en la base del conocimiento."""
        try:
            estado = self.gestion_poblacion.editarECA(diccionarioECA)
        except Exception as e:
            logger.error("Error al editar el ECA: " + str(e))            
            return {"status": "Fallo en la edición ECA"}        
        return {"status": "Edición ECA exitosa"}
        
class PoblacionOntologiaUsuarioService:
    """Servicio de Población para la Ontología del usuario."""
    #def __init__(self, gestion_base_conocimiento: IPoblacionPerfilUsuario):
    #    self.gestion_base_conocimiento = gestion_base_conocimiento    
    def cargarOntologia(self, file_content: bytes, nombre: str, ip_coordinador: str) -> None:
        """Guarda la ontología del perfil de usuario recibida."""
        logger.info(f"Cargando ontología para el usuario: {nombre} desde IP: {ip_coordinador}")
        try:            
            rutaArchivo = config.pathOWL + nombre
            self.pathActual = rutaArchivo
            if  os.path.exists(self.pathActual):
                logger.info(f"El archivo de ontología ya existe. Se reemplazará: {self.pathActual}")
                os.remove(self.pathActual)
            archivo=open(rutaArchivo,'wb')
            archivo.write(file_content)
            archivo.close()

            ##TODO guardar la ip del coordinador en un archivo para futuras consultas
            #AppUtil.guardarIpCoordinadorEnArchivo(ipCoordinador)
            #except Exception as e :

            #self.activarEcasUsuario()

        except Exception as e :
            logger.error("Error al cargar la ontología del perfil de usuario: " + str(e))    
        