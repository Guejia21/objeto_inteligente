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
    
class ConsultasOntologiaUsuarioService:
    """Servicio de Consultas para la Ontología del usuario."""
    def __init__(self, gestion_base_conocimiento: IConsultasPerfilUsuario):
        self.gestion_base_conocimiento = gestion_base_conocimiento