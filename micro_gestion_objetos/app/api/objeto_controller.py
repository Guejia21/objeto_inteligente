"""
    @file objeto_controller.py
    @brief Controlador REST para gestión de objetos inteligentes.
    @details
    Proporciona endpoints para operaciones CRUD y consultas sobre objetos inteligentes.
    Los endpoints disponibles son:
    - GET /objeto/Identificator: obtener metadatos del objeto
    - POST /objeto/StartObject: iniciar/crear un nuevo objeto inteligente
    - GET /objeto/SendState: obtener estado actual de datastreams
    - GET /objeto/SendData: enviar datos al objeto
    - GET /objeto/SendServiceState: verificar disponibilidad del servicio
    
    @note Todos los endpoints requieren validación de osid (ID del objeto inteligente).
    @note Las operaciones asincrónicas usan asyncio.to_thread() para operaciones bloqueantes.
    
    @author  NexTech
    @version 1.0
    @date 2025-01-10
    
    @see ObjetoService Para lógica de negocio
    @see docs/diagrams/flow_diagrams.md Para diagramas de secuencia
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse

from application.objeto_service import ObjetoService
from deps import get_objeto_service
from application.dtos import ObjectData


router = APIRouter(prefix="/objeto", tags=["Gestión de objeto inteligente"])
"""@var router Router principal para endpoints de objeto inteligente."""

@router.get("/Identificator")
async def get_identificator(osid: str = Query(..., description="ID del objeto inteligente"), objeto_service: ObjetoService = Depends(get_objeto_service)):
    """
        @brief Obtiene los metadatos del objeto inteligente.
        
        @param osid Identificador único del objeto inteligente (OSID).
        @param objeto_service Instancia del servicio de objetos (inyectada por dependencia).
        
        @return JSONResponse con status 200 y metadatos del objeto si es exitoso,
                o error 400/500 si falla.
        
        @exception ValueError Si el osid no es válido.
        @exception RuntimeError Si hay error en la persistencia.
        
        @details
        Flujo:
        1. Valida que el osid coincida con el objeto inteligente activo
        2. Verifica que existan metadatos en persistencia
        3. Retorna los metadatos en formato JSON
        4. Registra logs y eventos en el panel MQTT
        
        @see ObjetoService.getIdentificator()
        
        @example
        GET /objeto/Identificator?osid=obj_001
        200 OK
        {
            "status": "success",
            "message": "Metadatos del objeto inteligente obtenidos correctamente.",
            "data": {"id": "obj_001", "title": "Sensor Temperatura", ...}
        }
    """
    try:
        return await objeto_service.getIdentificator(osid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/StartObject")
async def start_object(data: ObjectData, objeto_service: ObjetoService = Depends(get_objeto_service)):
    """
        @brief Inicia un nuevo objeto inteligente con datos proporcionados.
        
        @param data DTO ObjectData con configuración del objeto (feed, datastreams, etc.)
        @param objeto_service Servicio de objetos (inyectado).
        
        @return JSONResponse con status 200 si es exitoso, o error 400/500.
        
        @exception ValueError Si los datos del DTO son inválidos.
        @exception RuntimeError Si falla poblar ontología o persistencia.
        
        @details
        Operación compuesta que:
        1. Verifica que la ontología no esté ya activa
        2. Estructura los datos del objeto inteligente
        3. Puebla la ontología (crea individuos y relaciones OWL)
        4. Persiste metadatos en JSON/DB
        5. Crea dispositivo en ThingsBoard (IoT Platform)
        6. Registra datastreams en microservicio_data_stream
        7. Registra evento en panel MQTT
        
        @note Esta es una operación distribuida que requiere coordinación entre
              múltiples microservicios. Considerar implementar saga/compensación.
        
        @see ObjetoService.startObject()
        @see docs/diagrams/flow_diagrams.md (StartObject sequence diagram)
        
        @example
        POST /objeto/StartObject
        Content-Type: application/json
        {
            "feed": {
                "id": "obj_sensor_001",
                "title": "Sensor Temperatura Sala",
                "description": "Sensor DHT22 en sala A",
                "datastreams": ["temp", "humidity"]
            }
        }
        
        200 OK
        {
            "status": "success",
            "message": "Objeto inteligente iniciado con éxito.",
            "data": {}
        }
    """
    try:
        return await objeto_service.startObject(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/SendState")
async def get_state(osid: str = Query(..., description="ID del objeto inteligente"), objeto_service: ObjetoService = Depends(get_objeto_service)):
    """
        @brief Obtiene el estado actual de los datastreams del objeto inteligente.
        
        @param osid Identificador único del objeto inteligente.
        @param objeto_service Servicio de objetos.
        
        @return JSONResponse con status 200 y estado de datastreams (valores, tipos, timestamps).
        
        @exception ValueError Si osid es inválido.
        @exception RuntimeError Si falla la consulta al microservicio datastream.
        
        @details
        Flujo:
        1. Valida que osid coincida con el objeto inteligente activo
        2. Delega consulta a microservicio_data_stream.send_state()
        3. Normaliza la respuesta (mapea campos a estructura uniforme)
        4. Opcionalmente enriquece con consultas a ontología
        5. Retorna estado normalizado
        
        @note Usa asyncio.to_thread() para no bloquear event loop si cliente HTTP es síncrono.
        
        @see ObjetoService.get_state()
        @see docs/diagrams/flow_diagrams.md (GetState sequence diagram)
        
        @example
        GET /objeto/SendState?osid=obj_001
        
        200 OK
        {
            "status": "success",
            "osid": "obj_001",
            "datastreams": [
                {"variableEstado": "temp", "type": "float", "valor": 23.5, "dstype": "sensor"},
                {"variableEstado": "humidity", "type": "float", "valor": 65.2, "dstype": "sensor"}
            ],
            "timestamp": "2025-01-10T15:30:45Z"
        }
    """
    try:
        return await objeto_service.get_state(osid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/SendData")
async def send_data(
    osid: str = Query(..., description="ID del objeto inteligente"),
    variableEstado: str = Query(..., description="Variable del estado a enviar"),
    tipove: str = Query('1', description="Tipo de variable (1=actuador, 2=sensor, etc.)"),
    objeto_service: ObjetoService = Depends(get_objeto_service)
):
    """
        @brief Envía datos a un datastream específico del objeto inteligente.
        
        @param osid Identificador único del objeto inteligente.
        @param variableEstado Nombre/ID del datastream (p. ej. 'temp', 'humidity').
        @param tipove Tipo de variable: '1' (actuador), '2' (sensor), etc.
        @param objeto_service Servicio de objetos.
        
        @return JSONResponse con status 200 y resultado de envío.
        
        @exception ValueError Si osid o variableEstado son inválidos.
        @exception RuntimeError Si falla la comunicación con microservicio datastream.
        
        @details
        Flujo:
        1. Valida que osid coincida con el objeto activo
        2. Verifica que variableEstado no esté vacío
        3. Delega en dataStream_service.send_data() con asyncio.to_thread()
        4. Registra log en panel MQTT
        5. Retorna respuesta normalizada
        
        @see ObjetoService.send_data()
        @see microservicio_data_stream Para documentación de datastreams
        
        @example
        GET /objeto/SendData?osid=obj_001&variableEstado=temp&tipove=1
        
        200 OK
        {"status": "success", "datastream": "temp", "sent": true}
    """
    try:
        return await objeto_service.send_data(osid, variableEstado, tipove)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/SendServiceState")
async def send_service_state(osid: str = Query(..., description="ID del objeto inteligente"), objeto_service: ObjetoService = Depends(get_objeto_service)):
    """
        @brief Verifica la disponibilidad/salud del microservicio de datastreams.
        
        @param osid Identificador del objeto inteligente (se incluye en respuesta si se proporciona).
        @param objeto_service Servicio de objetos.
        
        @return JSONResponse con status 200 y disponibilidad del servicio.
        
        @exception RuntimeError Si falla la comprobación de salud del servicio.
        
        @details
        Flujo:
        1. Ejecuta healthcheck contra microservicio_data_stream
        2. Retorna boolean indicando disponibilidad
        3. Opcionalmente incluye osid en respuesta
        
        @note No requiere validación de osid contra el objeto activo
              (es un check genérico de disponibilidad de servicio).
        
        @see ObjetoService.send_service_state()
        
        @example
        GET /objeto/SendServiceState?osid=obj_001
        
        200 OK
        {"service_available": true, "osid": "obj_001"}
    """
    try:
        return await objeto_service.send_service_state(osid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
