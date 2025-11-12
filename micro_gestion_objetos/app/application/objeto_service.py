
import json
from infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT
from domain.ObjetoInteligente import ObjetoInteligente
from infraestructure.logging.Logging import logger
from application.dtos import ObjectData
from config import settings
from infraestructure.IRepository import IRepository
from application import ontology_service


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
        json_data_object = self.objetoInteligente.estructurarJSON(data.feed.model_dump())
        logger.info("Iniciando la población de la ontología.")
        print(json_data_object)
        if not ontology_service.poblate_ontology(json_data_object):
            logger.error("Error al poblar la ontología.")
            return {"message": "Error al iniciar el objeto inteligente."}
        logger.info("Ontología poblada con éxito.")
        #Actualizar los datos del objeto
        self.objetoInteligente.update_attributes(data.feed.id, data.feed.title)
        #logger.debug("Datos estructurados para poblar la ontología: %s", json_data_object)
        self.persistence.save_object_metadata(json_data_object)
        #Después de instanciar la ontología y metadatos, se deben enviar los datastreams para que sean registrados en el micro de recursos y datastreams
        await self.log_panel.Publicar(settings.REGISTER_DATASTREAMS_QUEUE_NAME, json.dumps(json_data_object))
        logger.info("Objeto inteligente iniciado con éxito.")
        return {"message": "Objeto inteligente iniciado con éxito"}
    
    async def get_state(self, osid: int):
        """Obtiene el estado actual de los datastreams del objeto inteligente dado su osid."""
        if osid != self.objetoInteligente.osid:
            raise ValueError("El osid solicitado no coincide con el del objeto inteligente.")
        
        estado = ontology_service.get_datastream_states()
        if estado is None:
            raise ValueError("No se han recibido datos de datastreams para este objeto.")
        
        datastreams = [
            {
                "variableEstado": ds.get("datastream_id"),
                "type": ds.get("type", "float"),
                "valor": ds.get("valor"),
                "dstype": ds.get("dstype", "sensor")
            }
            for ds in estado
        ]
        return {"osid": osid, "datastreams": datastreams}

    async def send_data(self, osid: int, variableEstado: bool, tipove: str):
        """Envía datos al objeto inteligente."""
        if osid != self.objetoInteligente.osid:
            raise ValueError("El osid solicitado no coincide con el del objeto inteligente.")
        
        resultado = ontology_service.send_data(osid, variableEstado, tipove)
        if not resultado:
            raise RuntimeError("Error al enviar los datos al objeto inteligente.")
        return {"message": "Datos enviados correctamente al objeto inteligente."}
                





            
