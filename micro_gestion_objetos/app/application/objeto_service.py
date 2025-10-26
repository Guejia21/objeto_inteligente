
from app.infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT
from app.domain.ObjetoInteligente import ObjetoInteligente
from app.infraestructure.logging.Logging import logger
from app.application.dtos import ObjectData
from app.infraestructure.IRepository import IRepository
from app.application import ontology_service


class ObjetoService:
    def __init__(self, log_panel: ILogPanelMQTT, persistence: IRepository):
        self.log_panel = log_panel
        self.objetoInteligente = self.__initializeObjetoInteligente()
        self.persistence = persistence
    def __initializeObjetoInteligente(self) -> ObjetoInteligente:
        """Si la ontología existe, se inicializa el objeto inteligente con los datos guardados"""
        if ontology_service.is_active():
            osid = ontology_service.get_id()
            title = ontology_service.get_title()
            objeto = ObjetoInteligente(osid, title)
            logger.info("Objeto inteligente inicializado con ontología activa y osid %s", osid)
            return objeto
        else:
            logger.warning("La ontología no está activa. Objeto inteligente no inicializado.")
            return ObjetoInteligente(None)

    async def getIdentificator(self, osid: int):
        await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, "Enviando Metadata.json")
        await self.log_panel.PubLog("metadata_query", self.objetoInteligente.osid, self.objetoInteligente.title, self.objetoInteligente.osid, self.objetoInteligente.title,
                                     "metadata_query", "Solicitud Recibida")
        #Si el osid coincide con el del objeto inteligente guardado, se retorna su info
        if osid == self.objetoInteligente.osid:
            logger.info("Enviando identificador del objeto con oid %s", osid)
            try:
                if not self.persistence.is_object_metadata_exists():
                    logger.warning("Los metadatos del objeto no existen")
                    return None                
                resultado = self.persistence.get_object_metadata()                                
                await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, "Solicitud entregada")
                logger.info("Identificador enviado correctamente")
                await self.log_panel.PubLog("metadata_query", self.objetoInteligente.osid, self.objetoInteligente.title, self.objetoInteligente.osid, self.objetoInteligente.title,
                                "metadata_query", "Publicando Respuesta")                
                return resultado
            except Exception as e:
                logger.error("Error al leer el archivo de metadata: %s", e)                
                #TODO: Retornar un JSON estructurado (como ellos hacian con XML) con el error relacionado
                return None
        else:
            logger.warning("El osid solicitado %s no coincide con el del objeto inteligente %s", osid, self.objetoInteligente.osid)
            return {"message": "El osid solicitado no coincide con el del objeto inteligente."}
    async def startObject(self, data: ObjectData):
        """Método para iniciar el objeto inteligente con los datos proporcionados"""        
        if ontology_service.is_active():
            logger.warning("El objeto inteligente ya está activo.")
            return {"message": "El objeto inteligente ya está activo."}
        json_data_object = self.objetoInteligente.estructurarJSON(data.model_dump())
        logger.info("Iniciando la población de la ontología.")
        if not ontology_service.poblate_ontology(json_data_object):
            logger.error("Error al poblar la ontología.")
            return {"message": "Error al iniciar el objeto inteligente."}
        logger.info("Ontología poblada con éxito.")
        #Actualizar los datos del objeto
        self.objetoInteligente.update_attributes(data.feed.id, data.feed.title)        
        self.persistence.save_object_metadata(json_data_object)
        #TODO: Iniciar la persistencia de los datastreams
        logger.info("Objeto inteligente iniciado con éxito.")
        return {"message": "Objeto inteligente iniciado con éxito"}
            
        