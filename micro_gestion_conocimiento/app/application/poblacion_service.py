import os
from infraestructure.interfaces import IPoblacionPerfilUsuario
from infraestructure.interfaces.IPoblacion import IPoblacion
from infraestructure.logging.Logging import logger
from fastapi.responses import JSONResponse

from config import settings
from application.dtos import RegistroInteraccionDTO
from infraestructure.adaptadores.PoblarPerfilUsuario import PoblarPerfilUsuario

class PoblacionService:
    """Clase base para servicios de población."""
    
    def __init__(self, gestion_poblacion: IPoblacion):
        self.gestion_poblacion = gestion_poblacion

    def poblar_metadatos_objeto(self, diccionarioObjeto:dict, listaRecursos:dict ) -> None:
        """Pobla los metadatos del objeto inteligente en la base de conocimiento."""
        print(diccionarioObjeto)
        print(listaRecursos)
        if self.gestion_poblacion.poblarMetadatosObjeto(diccionarioObjeto, listaRecursos):
            return JSONResponse(
                status_code=201,
                content={"status": "Población exitosa"}
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"status": "Fallo en la población"}
            )
    def poblar_eca(self, diccionarioECA:dict) -> JSONResponse:
        """Pobla las reglas ECA en la base de conocimiento."""
        if self.gestion_poblacion.poblarECA(diccionarioECA):
            return JSONResponse(
                status_code=201,
                content={"status": "Población ECA exitosa"}
                )
        else:
            return JSONResponse(
                status_code=400,
                content={"status": "Fallo en la población ECA"}
            )
    def editar_eca(self, diccionarioECA:dict) -> JSONResponse:
        """Edita un ECA en la base del conocimiento."""
        try:
            estado = self.gestion_poblacion.editarECA(diccionarioECA)
        except Exception as e:
            logger.error("Error al editar el ECA: " + str(e))            
            return JSONResponse(
                status_code=400,
                content={"status": "Fallo en la edición ECA"}
            )
        return JSONResponse(
            status_code=200,
            content={"status": "Edición ECA exitosa"}
        )
        
class PoblacionOntologiaUsuarioService:
    """Servicio de Población para la Ontología del usuario."""
    def __init__(self, gestion_base_conocimiento: IPoblacionPerfilUsuario = None):
        self.gestion_base_conocimiento = gestion_base_conocimiento    
    def cargarOntologia(self, file_content: bytes, nombre: str, ip_coordinador: str) -> JSONResponse:
        """Guarda la ontología del perfil de usuario recibida."""
        logger.info(f"Cargando ontología para el usuario: {nombre} desde IP: {ip_coordinador}")
        try:            
            rutaArchivo = settings.PATH_PU_OWL + nombre
            self.pathActual = rutaArchivo
            if  os.path.exists(self.pathActual):
                logger.info(f"El archivo de ontología ya existe. Se reemplazará: {self.pathActual}")
                os.remove(self.pathActual)
            archivo=open(rutaArchivo,'wb')
            archivo.write(file_content)
            archivo.close()
            logger.info(f"Ontología guardada correctamente en: {rutaArchivo}")
            return JSONResponse(
                status_code=201,
                content={"status": "Ontología cargada exitosamente"}
            )           

        except Exception as e :
            logger.error("Error al cargar la ontología del perfil de usuario: " + str(e))    
            return JSONResponse(
                status_code=500,
                content={"status": "Error al cargar la ontología"}
            )
    def registroInteraccionUsuarioObjeto(self, data:RegistroInteraccionDTO) -> JSONResponse:
        """Registra una interacción del usuario con un objeto."""
        #Se inicializa de la misma manera que en el sistema legado
        self.gestion_base_conocimiento = PoblarPerfilUsuario(data.mac,data.email,"CARGAR")
        if self.gestion_base_conocimiento.registroInteraccionUsuarioObjeto(data.email, data.idDataStream, data.comando, data.osid, data.dateInteraction):
            return JSONResponse(
                status_code=201,
                content={"status": "Interacción registrada exitosamente"}
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"status": "Fallo al registrar la interacción"}
            )
    def eliminarOntologia(self)->JSONResponse:
        """Elimina la ontología del perfil de usuario."""
        try:
            if os.path.exists(settings.ONTOLOGIA_PU):
                os.remove(settings.ONTOLOGIA_PU)
                logger.info(f"Ontología eliminada correctamente: {settings.ONTOLOGIA_PU}")
            return JSONResponse(
                status_code=200,
                content={"status": "Ontología eliminada exitosamente"}
            )
        except Exception as e:
            logger.error("Error al eliminar la ontología del perfil de usuario: " + str(e))    
            return JSONResponse(
                status_code=500,
                content={"status": "Error al eliminar la ontología"}
            )