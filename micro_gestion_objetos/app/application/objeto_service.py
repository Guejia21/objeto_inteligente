
from app.infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT
from app.domain.ObjetoInteligente import ObjetoInteligente
from app.infraestructure.logging.Logging import logger
from app.application.dtos import ObjectData
from app.infraestructure.IRepository import IRepository
from app.application import ontology_service
from app.application import dataStream_service
import asyncio


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
        if not ontology_service.poblate_ontology(json_data_object):
            print(json_data_object)
            logger.error("Error al poblar la ontología.")
            return {"message": "Error al iniciar el objeto inteligente."}
        logger.info("Ontología poblada con éxito.")
        #Actualizar los datos del objeto
        self.objetoInteligente.update_attributes(data.feed.id, data.feed.title)        
        self.persistence.save_object_metadata(json_data_object)
        #TODO: Iniciar la persistencia de los datastreams
        logger.info("Objeto inteligente iniciado con éxito.")
        return {"message": "Objeto inteligente iniciado con éxito"}

    async def get_state(self, osid: str):
        """Obtiene el estado actual de los datastreams del objeto inteligente.

        Esta implementación delega la obtención de estado al microservicio de
        datastreams mediante `dataStream_service.send_state` y normaliza la
        respuesta para mantener la forma esperada por la API.
        """
        if osid != self.objetoInteligente.osid:
            logger.warning("El osid solicitado %s no coincide con el del objeto inteligente %s", osid, self.objetoInteligente.osid)
            raise ValueError("El osid solicitado no coincide con el del objeto inteligente.")

        try:
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, "Inicio SendState")
            logger.info("Solicitando estado de datastreams al microservicio para osid %s", osid)

            # Ejecutar la llamada bloquente en un hilo para no bloquear el event loop
            resultado = await asyncio.to_thread(dataStream_service.send_state, str(osid))

            if not isinstance(resultado, dict):
                logger.error("Respuesta inesperada de dataStreamService: %s", resultado)
                raise ValueError("Respuesta inválida del servicio de datastreams")

            datastreams = resultado.get("datastreams")
            if datastreams is None:
                logger.error("La respuesta de SendState no contiene 'datastreams': %s", resultado)
                raise ValueError("Respuesta inválida del servicio de datastreams: sin datastreams")

            normalized = []
            for ds in datastreams:
                normalized.append({
                    "variableEstado": ds.get("datastream_id") or ds.get("datastream") or ds.get("id"),
                    "type": ds.get("datastream_format") or ds.get("datatype") or ds.get("type") or "string",
                    "valor": ds.get("value") or ds.get("valor") or ds.get("current_value"),
                    "dstype": ds.get("datastream_type") or ds.get("dstype") or "sensor"
                })

            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, "SendState Fin")
            logger.info("SendState exitoso para %d datastreams", len(normalized))

            return {"osid": resultado.get("osid", osid), "datastreams": normalized, "timestamp": resultado.get("timestamp")}

        except Exception as e:
            logger.error("Error obteniendo estado de datastreams desde dataStreamService: %s", e)
            raise ValueError(f"Error al obtener estado: {e}")
    
    async def send_service_state(self, osid: str = None):
        """Consulta la disponibilidad del microservicio de datastream.

        Nota: el endpoint de datastream (`send_service_state`) no requiere
        `osid`, por lo que aquí ignoramos el parámetro si se pasa desde la
        ruta y delegamos directamente en `dataStream_service`.
        """
        try:
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, "Inicio SendServiceState")
            # Ejecutar la comprobación del servicio en hilo (función sincrónica)
            available = await asyncio.to_thread(dataStream_service.send_service_state)
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, "SendServiceState Fin")
            # Devolver disponibilidad; incluimos osid solo si fue provisto por la ruta
            result = {"service_available": bool(available)}
            if osid:
                result["osid"] = osid
            return result
        except Exception as e:
            logger.error("Error verificando estado del servicio de datastreams: %s", e)
            raise ValueError(f"Error al verificar servicio de datastreams: {e}")

    async def send_data(self, osid: str, variableEstado: str, tipove: str = '1'):
        """Solicita al microservicio de datastream el valor de un datastream espSecífico."""
        if osid != self.objetoInteligente.osid:
            logger.warning("El osid solicitado %s no coincide con el del objeto inteligente %s", osid, self.objetoInteligente.osid)
            raise ValueError("El osid solicitado no coincide con el del objeto inteligente.")

        if not variableEstado:
            raise ValueError("variableEstado es requerido")

        try:
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, f"Inicio SendData {variableEstado}")
            # Ejecutar la petición SendData en un hilo para evitar bloqueo
            resultado = await asyncio.to_thread(dataStream_service.send_data, str(osid), str(variableEstado), tipove)
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, f"SendData Fin {variableEstado}")
            return resultado
        except Exception as e:
            logger.error("Error en SendData para %s/%s: %s", osid, variableEstado, e)
            raise ValueError(f"Error al solicitar SendData: {e}")
                
        





            
