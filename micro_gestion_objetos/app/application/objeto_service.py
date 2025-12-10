"""
    @file objeto_service.py
    @brief Servicio de lógica de negocio para gestión de objetos inteligentes.
    @details
    Implementa la capa de aplicación (Application Service pattern) que orquesta
    la creación, consulta y actualización de objetos inteligentes.
    
    Responsabilidades:
    - Validación de datos de entrada (DTOs)
    - Orquestación de múltiples servicios (persistencia, ontología, datastream, IoT)
    - Gestión de errores y retries
    - Implementación de patrones saga/compensación para operaciones compuestas
    - Logging y observabilidad (panel MQTT, correlation ID)
    
    Patrones utilizados:
    - Service Locator / Dependency Injection (FastAPI Depends)
    - Adapter (normalización de respuestas de servicios externos)
    - Async/Await (asyncio) para operaciones no bloqueantes
    - asyncio.to_thread() para operaciones bloqueantes (clientes HTTP síncronos)
    
    @note Cada instancia mantiene en memoria la ontología cargada del objeto inteligente activo.
    @note Las operaciones que llamam a servicios remotos están envueltas en try/except
          y registran logs detallados para debugging.
    
    @author NexTech
    @version 1.0
    @date 2025-01-10
    
    @see ObjetoInteligente Para el modelo de dominio
    @see IRepository Para persistencia
    @see microservicio_data_stream Para gestión de datastreams
    @see micro_gestion_conocimiento Para operaciones de ontología
    @see docs/diagrams/flow_diagrams.md Para diagramas de secuencia de procesos
"""

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
    """
        @class ObjetoService
        @brief Servicio de aplicación para operaciones sobre objetos inteligentes.
        
        @details
        Implementa la lógica de negocio de alto nivel para:
        - Inicialización de objetos inteligentes con ontología y datastreams
        - Consultas de metadatos y estado
        - Envío de datos a datastreams
        - Monitoreo de disponibilidad de servicios
        
        Patrón: Application Service (Clean Architecture) + Dependency Injection
        
        Atributos:
        - log_panel: cliente para publicar logs/eventos MQTT (ILogPanelMQTT)
        - objetoInteligente: modelo de dominio del objeto activo (ObjetoInteligente)
        - persistence: repositorio de persistencia (IRepository)
        
        @note Mantiene en memoria un único objeto inteligente activo por instancia.
              Para múltiples objetos, considerar refactorizar con pattern Registry.
        
        @see ObjetoInteligente Para dominio
        @see IRepository Para persistencia (JSON/DB)
        @see ILogPanelMQTT Para logging distribuido
        
        @author Sistema Objeto Inteligente
        @date 2025-01-10
    """
    def __init__(self, log_panel: ILogPanelMQTT, persistence: IRepository):
        """
            @brief Constructor del servicio de objeto inteligente.
            
            @param log_panel Instancia del cliente MQTT para publicar logs y eventos.
            @param persistence Instancia del repositorio de persistencia (JSON/DB).
            
            @details
            Inicializa el servicio y carga el objeto inteligente desde la ontología
            si existe una activa; si no, crea una instancia vacía y registra warning.
            
            @see __initializeObjetoInteligente()
        """
        self.log_panel = log_panel
        self.objetoInteligente = self.__initializeObjetoInteligente()
        self.persistence = persistence
    def __initializeObjetoInteligente(self) -> ObjetoInteligente:
        """
            @brief Inicializa el objeto inteligente desde la ontología activa.
            
            @return Instancia de ObjetoInteligente con datos de la ontología, o vacía.
            
            @details
            Si la ontología está activa (cargada en memoria), recupera el OSID
            y título, crea un modelo de dominio y registra log INFO.
            Si no está activa, crea una instancia vacía y registra warning.
            
            @note Invocado desde __init__. Considerar hacerlo async si la carga
                  de ontología requiere I/O.
            
            @see ontology_service.is_active()
            @see ontology_service.get_id()
            @see ontology_service.get_title()
        """
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
        """
            @brief Obtiene los metadatos del objeto inteligente.
            
            @param osid Identificador único del objeto inteligente (debe coincidir con el activo).
            
            @return JSONResponse con status 200 y metadatos si existe, o error 400/500.
            
            @exception ValueError Si osid no coincide.
            @exception RuntimeError Si falla la lectura de persistencia.
            
            @details
            Flujo:
            1. Valida que el osid coincida con el objeto activo
            2. Publica log raw en panel MQTT (inicio solicitud)
            3. Verifica que los metadatos existan en persistencia
            4. Retorna los metadatos en formato JSON con status 200
            5. Publica log de respuesta en panel MQTT
            
            Si el osid no coincide, retorna error 400.
            Si hay error al leer metadatos, retorna error 500.
            
            @see persistence.is_object_metadata_exists()
            @see persistence.get_object_metadata()
            @see log_panel.PubRawLog()
            @see log_panel.PubLog()
            
            @example
            200 OK:
            {
                "status": "success",
                "message": "Metadatos del objeto inteligente obtenidos correctamente.",
                "data": {
                    "id": "obj_001",
                    "title": "Sensor Temperatura Sala A",
                    "datastreams": [...],
                    ...
                }
            }
        """
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
        """
            @brief Inicia un nuevo objeto inteligente con datos proporcionados.
            
            @param data DTO ObjectData con configuración: feed (id, title, datastreams, etc.)
            
            @return JSONResponse con status 200 si exitoso, o error 400/500 si falla.
            
            @exception ValueError Si los datos del DTO son inválidos.
            @exception RuntimeError Si falla la población de ontología o persistencia.
            
            @details
            Operación compuesta y distribuida que:
            
            1. Valida que la ontología no esté ya activa (evita reinicios)
            2. Estructura los datos en formato JSON compatible con el objeto inteligente
            3. Puebla la ontología en micro_gestion_conocimiento (crea individuos OWL)
            4. Actualiza los atributos del modelo de dominio en memoria
            5. Persiste metadatos en JSON/DB mediante repositorio
            6. Crea dispositivo en ThingsBoard (IoT Platform) y obtiene token
            7. Publica mensaje en cola MQTT para que microservicio_data_stream
               registre los datastreams
            8. Registra eventos en panel MQTT para auditoría
            
            @note Esta es una operación **distribuida** que involucra múltiples
                  microservicios. Si algún paso falla (ej. ThingsBoard no disponible),
                  la ontología ya fue poblada y los metadatos ya se persistieron.
                  Considerar implementar saga/compensación o transacciones distribuidas.
            
            @warning Si la población de ontología falla, retorna error 500.
                     Posterior ejecución puede intentar reintentar con idempotencia.
            
            @see ontology_service.poblate_ontology()
            @see persistence.save_object_metadata()
            @see tb_client.create_device_with_token() Para ThingsBoard
            @see log_panel.Publicar() Para cola de datastreams
            @see docs/diagrams/flow_diagrams.md (StartObject sequence diagram)
            
            @example
            POST /objeto/StartObject
            {
                "feed": {
                    "id": "obj_sensor_001",
                    "title": "Sensor Temperatura Sala",
                    "description": "Sensor DHT22",
                    "datastreams": ["temp", "humidity"]
                }
            }
            
            200 OK:
            {
                "status": "success",
                "message": "Objeto inteligente iniciado con éxito.",
                "data": {}
            }
        """        
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
                
        





            
