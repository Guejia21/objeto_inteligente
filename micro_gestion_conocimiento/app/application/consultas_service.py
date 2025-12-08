from typing import Any, List

from fastapi.responses import JSONResponse
from infraestructure.interfaces.IConsultasPerfilUsuario import IConsultasPerfilUsuario
from infraestructure.logging.Logging import logger
from infraestructure.interfaces.IConsultas import IConsultasOOS

class ConsultasService:
    """Servicio de Consultas para la Ontología OOS."""
    def __init__(self, gestion_base_conocimiento: IConsultasOOS):
        self.gestion_base_conocimiento = gestion_base_conocimiento
    def consultarOntoActiva(self):
        """Verifica que la ontología instanciada esté disponible; lanza excepción si no lo está."""
        if not self.gestion_base_conocimiento.consultarOntoActiva():
            logger.warning("La ontología no está activa o disponible.")
            return False
        return True
    def consultarId(self):
        """Devuelve el id del objeto (consulta SPARQL sobre oos:id_object)."""
        return self.gestion_base_conocimiento.consultarId()
    
    def consultarDescription(self):
        """Retorna la descripción asociada al State del objeto."""
        return self.gestion_base_conocimiento.consultarDescription()

    def consultarPrivate(self):
        """Retorna si el feed/objeto es privado (oos:private)."""
        return self.gestion_base_conocimiento.consultarPrivate()

    def consultarTitle(self):
        """Retorna el título descriptivo del State (oos:title)."""
        return self.gestion_base_conocimiento.consultarTitle()

    def consultarFeed(self):
        """Retorna la URL del feed asociada al State (oos:feed)."""
        return self.gestion_base_conocimiento.consultarFeed()

    def consultarStatus(self):
        """Retorna el estado (status) del State del objeto."""
        return self.gestion_base_conocimiento.consultarStatus()

    def consultarUpdated(self):
        """Retorna la fecha/hora de la última actualización del State (oos:updated)."""
        return self.gestion_base_conocimiento.consultarUpdated()

    def consultarCreated(self):
        """Retorna la fecha de creación del State (oos:created)."""
        return self.gestion_base_conocimiento.consultarCreated()

    def consultarCreator(self):
        """Retorna el creador del State/objeto (oos:creator)."""
        return self.gestion_base_conocimiento.consultarCreator()

    def consultarVersion(self):
        """Retorna la versión asociada al State (oos:version)."""
        return self.gestion_base_conocimiento.consultarVersion()

    def consultarWebsite(self):
        """Retorna la URL de un sitio web relevante para el feed/objeto (oos:website)."""
        return self.gestion_base_conocimiento.consultarWebsite()

    def consultarServiceState(self):
        """Retorna el estado del servicio básico del objeto (oos:service_state)."""
        return self.gestion_base_conocimiento.consultarServiceState()

    def consultarTagsDatastream(self, idDatastream):
        """Obtiene los tags para un datastream dado (filtrado por datastream_id)."""
        return self.gestion_base_conocimiento.consultarTagsDatastream(idDatastream)

    def consultarUnitDatastream(self, idDatastream):
        """Obtiene la unidad (label y symbol) asociada a un datastream dado."""
        return self.gestion_base_conocimiento.consultarUnitDatastream(idDatastream)

    def consultarDatastreams(self, idDatastream):
        """Retorna metadatos completos de un datastream específico, incluyendo tags y unidad."""
        return self.gestion_base_conocimiento.consultarDatastreams(idDatastream)
    
    def consultarTagsTodosDatastreams(self):
        """Retorna los tags de todos los datastreams (lista de pares datastream_id, tag)."""
        return self.gestion_base_conocimiento.consultarTagsTodosDatastreams()

    def consultarUnitTodosDatastreams(self):
        """Retorna la unidad (label, symbol) para todos los datastreams como lista de diccionarios."""
        return self.gestion_base_conocimiento.consultarUnitTodosDatastreams()

    def consultarTodosDatastreams(self):
        """Retorna la lista completa de datastreams con sus metadatos y tags."""
        return self.gestion_base_conocimiento.consultarTodosDatastreams()

    def consultarListaIdDatastreams(self):
        """Retorna una lista con los identificadores de todos los datastreams."""
        return self.gestion_base_conocimiento.consultarListaIdDatastreams()

    def consultarLocation(self):
        """Retorna la localización del objeto como diccionario (lon, lat, name, domain, ele)."""
        return self.gestion_base_conocimiento.consultarLocation()

    def consultarState(self):
        """Retorna el State del objeto como diccionario con sus propiedades."""
        return self.gestion_base_conocimiento.consultarState()        
    
    def consultarTagsObjeto(self):
        """Retorna la lista de tags asociados al objeto/State."""
        return self.gestion_base_conocimiento.consultarTagsObjeto()

    def consultarDataStreamFormat(self):
        """Retorna el formato y tipo de todos los datastreams (datastream_id, datastream_format, datastream_type)."""
        return self.gestion_base_conocimiento.consultarDataStreamFormat()
    
    def consultarDataStreamFormatPorId(self, datastream_id):
        """Retorna el formato de un datastream específico por su datastream_id."""
        return self.gestion_base_conocimiento.consultarDataStreamFormatPorId(datastream_id)

    def consultarServiceIntelligent(self):
        """Retorna un diccionario con id, service_state y datastreams relacionados (consulta agregada)."""
        return self.gestion_base_conocimiento.consultarServiceIntelligent()
    
    def consultarMetodosSend(self):
        """Retorna instancias de métodos Send en la ontología (consulta de instancias)."""
        return self.gestion_base_conocimiento.consultarMetodosSend()

    def consultarMetodosReceive(self):
        """Retorna instancias de métodos Receive en la ontología (consulta de instancias)."""
        return self.gestion_base_conocimiento.consultarMetodosReceive()

    def consultarMetodosExternal(self):
        """Retorna instancias de métodos External en la ontología (consulta de instancias)."""
        return self.gestion_base_conocimiento.consultarMetodosExternal()
    def verficarContrato(self, osid:str,osidDestino : str):
        """Verifica si existe un contrato ECA entre dos objetos en la ontología.

        Args:
            osid (str): ID del objeto que envía la consulta.
            osidDestino (str): ID del objeto destino del contrato.

        Returns:
            _type_: Lista de diccionarios con la información del contrato si existe, o una lista vacía si no existe.
        """        
        return self.gestion_base_conocimiento.verificarContrato(osid,osidDestino)
    def setEcaState(self, valorNuevo:str, nombreECA:str):
        """Actualiza el estado de una ECA."""
        #El nuevo valor solo puede ser 'on' o 'off'
        if valorNuevo not in ['on', 'off']:
            logger.error(f"Valor inválido para el estado de ECA: {valorNuevo}. Debe ser 'on' o 'off'.")
            return {"error": "Valor inválido. Use 'on' o 'off'."}
        logger.info(f"Actualizando estado de ECA '{nombreECA}' a '{valorNuevo}'")
        self.gestion_base_conocimiento.setEcaState(valorNuevo, nombreECA)
        logger.info(f"Estado de ECA '{nombreECA}' actualizado correctamente.")
        return {"status": "ECA actualizada correctamente"}
    def listarECAs(self):
        """Retorna la lista de ECAs definidas en la ontología."""
        return self.gestion_base_conocimiento.listarEcas()
    def eliminarECA(self, nombreECA:str):        
        """
        Elimina una ECA de la ontología.
        
        :param self: Instancia del servicio de consultas.
        :param nombreECA: Nombre de la ECA a eliminar junto con el nombre del usuario (Ejemplo: ecausuario).
        :type nombreECA: str
        """
        self.gestion_base_conocimiento.eliminarEca(nombreECA)
        logger.info(f"ECA '{nombreECA}' eliminada correctamente.")
        return {"status": "ECA eliminada correctamente"}
    def listarDinamicEstado(self, eca_state:str):
        """
        Lista las ECAs con un estado específico.
        
        :param self: Instancia del servicio de consultas.
        :param eca_state: Estado específico de las ECAs a listar(on/off).
        :type eca_state: str
        """
        return self.gestion_base_conocimiento.listarDinamicEstado(eca_state)
    def setEcaListState(self, listaEcas: List[List[Any]]):
        """
        Actualiza el estado de una lista de ECAs.
        
        :param self: Instancia del servicio de consultas.
        :param listaEcas: Lista de nombres de ECAs a actualizar, su formato es una lista tipo ["name_eca","new_state"].
        :type listaEcas: List[List[Any]]
        """
        self.gestion_base_conocimiento.setEcaListState(listaEcas)
        logger.info(f"{len(listaEcas)} ECAs actualizadas correctamente.")
        return {"status": "ECAs actualizadas correctamente"}
class ConsultasOntologiaUsuarioService:
    """Servicio de Consultas para la Ontología del usuario."""
    def __init__(self, gestion_base_conocimiento: IConsultasPerfilUsuario):
        self.gestion_base_conocimiento = gestion_base_conocimiento
    def consultarActive(self)->JSONResponse:
        """Consulta si el perfil del usuario está activo en su ontología."""
        active = self.gestion_base_conocimiento.consultarActive() 
        if active is None:
            logger.warning("No se encontró el estado de actividad del usuario en la ontología.")
            return JSONResponse(content={"active": None}, status_code=404)
        return JSONResponse(content={"active": active}, status_code=200)
    def consultarEmailUsuario(self)->JSONResponse:
        """Consulta el email del usuario desde su ontología."""
        email = self.gestion_base_conocimiento.consultarEmailUsuario() 
        if not email:
            logger.warning("No se encontró el email del usuario en la ontología.")
            return JSONResponse(content={"email": ""}, status_code=404)
        return JSONResponse(content={"email": email}, status_code=200)
    def consultarListaPreferenciasporOSID(self, osid: str) -> JSONResponse:
        """Consulta la lista de preferencias del usuario por OSID."""
        preferencias = self.gestion_base_conocimiento.consultarListaPreferenciasporOSID(osid)
        if not preferencias:
            logger.warning(f"No se encontraron preferencias para el OSID: {osid}")
            return JSONResponse(content={"preferencias": []}, status_code=404)
        return JSONResponse(content={"preferencias": preferencias}, status_code=200)