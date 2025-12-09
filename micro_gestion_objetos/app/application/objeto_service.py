
import json

from fastapi.responses import JSONResponse
from infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT
from domain.ObjetoInteligente import ObjetoInteligente
from infraestructure.logging.Logging import logger
from application.dtos import ObjectData
from config import settings
from infraestructure.IRepository import IRepository
from application import ontology_service
from application import dataStream_service
from infraestructure.things_board import tb_client
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

    async def getIdentificator(self, osid: int)->JSONResponse:
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
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "message": "Metadatos del objeto inteligente obtenidos correctamente.",
                        "data": resultado
                    }
                )
            except Exception as e:
                logger.error("Error al leer el archivo de metadata: %s", e)                                
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": "Error al leer el archivo de metadata.",
                        "data": {}
                    }
                )
        else:
            logger.warning("El osid solicitado %s no coincide con el del objeto inteligente %s", osid, self.objetoInteligente.osid)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "El osid solicitado no coincide con el del objeto inteligente.",
                    "data": {}
                }
            )
    


    async def startObject(self, data: ObjectData)->JSONResponse:
        """Método para iniciar el objeto inteligente con los datos proporcionados"""        
        if ontology_service.is_active():
            logger.warning("El objeto inteligente ya está activo.")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "El objeto inteligente ya está activo.",
                    "data": {}
                }
            )
        json_data_object = self.objetoInteligente.estructurarJSON(data.feed.model_dump())
        logger.info("Iniciando la población de la ontología.")
        if not ontology_service.poblate_ontology(json_data_object):
            print(json_data_object)
            logger.error("Error al poblar la ontología.")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Error al poblar la ontología.",
                    "data": {}
                }
            )
        logger.info("Ontología poblada con éxito.")
        #Actualizar los datos del objeto
        self.objetoInteligente.update_attributes(data.feed.id, data.feed.title)        
        self.persistence.save_object_metadata(json_data_object)
        #Después de instanciar la ontología y metadatos, se deben enviar los datastreams para que sean registrados en el micro de recursos y datastreams
        #Se crea el dispositivo en thingsboard y se obtiene su token
        tb_client_token = tb_client.create_device_with_token(data.feed.id, data.feed.title)
        if tb_client_token:
            logger.info("Dispositivo creado en ThingsBoard con éxito.")
            #Agregar el token de thingsboard al JSON del objeto
            json_data_object['thingsboard_token'] = tb_client_token
        else:
            logger.error("Error al crear el dispositivo en ThingsBoard.")                    
        await self.log_panel.Publicar(settings.REGISTER_DATASTREAMS_QUEUE_NAME, json.dumps(json_data_object))    
        logger.info("Objeto inteligente iniciado con éxito.")
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Objeto inteligente iniciado con éxito.",
                "data": {}
            }
        )

    async def get_state(self, osid: str)->JSONResponse:
        """Obtiene el estado actual de los datastreams del objeto inteligente.

        Esta implementación delega la obtención de estado al microservicio de
        datastreams mediante `dataStream_service.send_state` y normaliza la
        respuesta para mantener la forma esperada por la API.
        """
        if osid != self.objetoInteligente.osid:
            logger.warning("El osid solicitado %s no coincide con el del objeto inteligente", osid)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "El osid solicitado no coincide con el del objeto inteligente.",
                    "data": {}
                }
            )

        try:
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, "Inicio SendState")
            logger.info("Solicitando estado de datastreams al microservicio para osid %s", osid)

            # Ejecutar la llamada bloquente en un hilo para no bloquear el event loop
            resultado = await asyncio.to_thread(dataStream_service.send_state, str(osid))

            if not isinstance(resultado, dict):
                logger.error("Respuesta inesperada de dataStreamService: %s", resultado)
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": "Respuesta inválida del servicio de datastreams.",
                        "data": {}
                    }
                )

            datastreams = resultado.get("datastreams")
            if datastreams is None:
                logger.error("La respuesta de SendState no contiene 'datastreams': %s", resultado)
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": "Respuesta inválida del servicio de datastreams: sin datastreams.",
                        "data": {}
                    }
                )

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

            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "osid": resultado.get("osid", osid),
                    "datastreams": normalized,
                    "timestamp": resultado.get("timestamp")
                }
            )

        except Exception as e:
            logger.error("Error obteniendo estado de datastreams desde dataStreamService: %s", e)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al obtener estado: {e}",
                    "data": {}
                }
            )
    
    async def send_service_state(self, osid: str = None)->JSONResponse:
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
            return JSONResponse(
                status_code=200,
                content=result
            )
        except Exception as e:
            logger.error("Error verificando estado del servicio de datastreams: %s", e)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al verificar servicio de datastreams: {e}",
                    "data": {}
                }
            )

    async def send_data(self, osid: str, variableEstado: str, tipove: str = '1')->JSONResponse:
        """Solicita al microservicio de datastream el valor de un datastream espSecífico."""
        if osid != self.objetoInteligente.osid:
            logger.warning("El osid solicitado %s no coincide con el del objeto inteligente %s", osid, self.objetoInteligente.osid)
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "El osid solicitado no coincide con el del objeto inteligente.",
                    "data": {}
                }
            )

        if not variableEstado:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "variableEstado es requerido",
                    "data": {}
                }
            )

        try:
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, f"Inicio SendData {variableEstado}")
            # Ejecutar la petición SendData en un hilo para evitar bloqueo
            resultado = await asyncio.to_thread(dataStream_service.send_data, str(osid), str(variableEstado), tipove)
            await self.log_panel.PubRawLog(self.objetoInteligente.osid, self.objetoInteligente.osid, f"SendData Fin {variableEstado}")
            return JSONResponse(
                status_code=200,
                content=resultado
            )
        except Exception as e:
            logger.error("Error en SendData para %s/%s: %s", osid, variableEstado, e)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al solicitar SendData: {e}",
                    "data": {}
                }
            )
                
        





            
