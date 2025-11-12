from fastapi import APIRouter, HTTPException, Query, File, Form, UploadFile
from typing import Dict, Any
import json
import logging
import httpx


from app.application.dtos.request_dtos import (
    CrearPreferenciaRequest,
    RecibirOntologiaRequest,
    NotificarSalidaRequest,
    RegistroInteraccionRequest
)
from app.domain.services.personalizacion_service import PersonalizacionService
from app.infrastructure.repositories.personalizacion_repository_impl import PersonalizacionRepositoryImpl  

logger = logging.getLogger(__name__)

# Configurar dependencias
try:
    repository = PersonalizacionRepositoryImpl()  # ✅ Usar la implementación concreta
    personalizacion_service = PersonalizacionService(repository)
    logger.info("✅ Dependencias del servicio de personalización inicializadas correctamente")
except Exception as e:
    logger.error(f"Error inicializando dependencias: {e}")
    personalizacion_service = None

# Configuración de microservicios
ONTOLOGIAS_MS_URL = "http://localhost:8002"  
AUTOMATIZACION_MS_URL = "http://localhost:8003"  

router = APIRouter()

@router.get("/CrearPreferencia")
async def crear_preferencia(
    email: str = Query(..., description="Email del usuario"),
    osid: str = Query(..., description="ID del objeto origen"),
    osidDestino: str = Query(..., description="ID del objeto destino"),
    contrato: str = Query(..., description="Contrato ECA en formato JSON")
):
    """
    Endpoint IDÉNTICO al sistema legacy - Crea una preferencia/ECA
    """
    try:
        if not personalizacion_service:
            raise HTTPException(status_code=500, detail="Servicio no disponible")
            
        logger.info(f" CrearPreferencia recibido - email: {email}, osid: {osid}")
        
        # Parsear contrato JSON (igual que en legacy)
        try:
            contrato_dict = json.loads(contrato)
        except json.JSONDecodeError as e:
            logger.error(f" Error parseando JSON del contrato: {e}")
            raise HTTPException(status_code=400, detail="Contrato JSON inválido")
        
        # Crear request DTO
        preferencia_request = CrearPreferenciaRequest(
            email=email,
            osid=osid,
            osidDestino=osidDestino,
            contrato=contrato_dict
        )
        
        # Llamar al servicio
        resultado = await personalizacion_service.crear_preferencia(preferencia_request)
        
        # Mantener compatibilidad con respuestas del legacy
        if resultado["status_code"] != 200:
            raise HTTPException(
                status_code=resultado["status_code"],
                detail=resultado["error"]
            )
        
        logger.info(f"Preferencia creada exitosamente para usuario: {email}")
        return resultado["mensaje"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en CrearPreferencia: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/RecibirOntologia")
async def recibir_ontologia(
    file: UploadFile = File(..., description="Archivo de ontología (.owl)"),    nombre: str = Form(..., description="Nombre de la ontología"),
    ipCoordinador: str = Form(..., description="IP del coordinador")
):
    """
    ENDPOINT DE PERSONALIZACIÓN - Recibe ontología y la envía al microservicio de ontologías
    """
    try:
        logger.info(f"Recibiendo ontología: {nombre} desde {ipCoordinador}")
        
        # Validar tipo de archivo
        if not file.filename.endswith('.owl'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos .owl")


        file_content = await file.read()

        # Enviar la ontología al microservicio de ontologías
        async with httpx.AsyncClient() as client:
            files = {
                'file': (file.filename, file_content, file.content_type or 'application/owl+xml')
            }
            data = {
                'nombre': nombre,
                'ipCoordinador': ipCoordinador
            }
            
            response = await client.post(
                f"{ONTOLOGIAS_MS_URL}/ontologias/cargar",
                files=files,
                data=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info(f"Ontología {nombre} enviada exitosamente al microservicio de ontologías")
                return {
                    "mensaje": "Ontología recibida y enviada al microservicio de ontologías exitosamente",
                    "status_code": 200,
                    "data": response.json()
                }
            else:
                logger.error(f" Error enviando ontología al microservicio: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error en microservicio de ontologías: {response.text}"
                )
    
    except httpx.RequestError as e:
        logger.error(f" Error de conexión con microservicio de ontologías: {e}")
        raise HTTPException(
            status_code=503,
            detail="Microservicio de ontologías no disponible"
        )
    except Exception as e:
        logger.error(f" Error procesando ontología: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/NotificarSalidaDeUsuario")
async def notificar_salida_usuario(
    osid: str = Form(..., description="ID del objeto/usuario")
):
    """
     ENDPOINT DE PERSONALIZACIÓN - HU-2: Notificación de salida de usuario
    Coordina con el microservicio de automatización para desactivar ECAs
    """
    try:
        logger.info(f" Notificando salida de usuario con osid: {osid}")
        
        if not personalizacion_service:
            raise HTTPException(status_code=500, detail="Servicio no disponible")
        
        # 1. Procesar lógica de personalización (limpiar preferencias, etc.)
        resultado_personalizacion = await personalizacion_service.procesar_salida_usuario(osid)
        
        # 2. Llamar al microservicio de automatización para desactivar ECAs
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AUTOMATIZACION_MS_URL}/automatizacion/ApagarTodosEcas",
                    params={"osid": osid},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f" ECAs desactivados para usuario {osid} via automatización")
                    resultado_automatizacion = response.json()
                else:
                    logger.warning(f" No se pudieron desactivar ECAs para {osid}: {response.status_code}")
                    resultado_automatizacion = {"error": "No se pudieron desactivar ECAs"}
        
        except httpx.RequestError as e:
            logger.warning(f" Microservicio de automatización no disponible: {e}")
            resultado_automatizacion = {"error": "Servicio de automatización no disponible"}
        
        return {
            "mensaje": "Salida de usuario procesada exitosamente",
            "osid": osid,
            "personalizacion": resultado_personalizacion,
            "automatizacion": resultado_automatizacion,
            "status_code": 200
        }
        
    except Exception as e:
        logger.error(f" Error notificando salida de usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/RegistroInteraccionUsuarioObjeto")
async def registro_interaccion_usuario_objeto(
    email: str = Form(..., description="Email del usuario"),
    idDataStream: str = Form(..., description="ID del data stream"),
    comando: str = Form(..., description="Comando de interacción"),
    osid: str = Form(..., description="ID del objeto"),
    mac: str = Form(..., description="Dirección MAC del dispositivo"),
    dateInteraction: str = Form(..., description="Fecha de interacción (ISO format)")
):
    """
    Registra interacciones entre usuarios y objetos
    """
    try:
        logger.info(f"Registrando interacción: usuario {email} con objeto {osid}")
        
        resultado = await personalizacion_service.registrar_interaccion(
            email=email,
            id_data_stream=idDataStream,
            comando=comando,
            osid=osid,
            mac=mac,
            date_interaction=dateInteraction
        )
        
        return {"mensaje": "Interacción registrada exitosamente", "status_code": 200, "data": resultado}
    
    except Exception as e:
        logger.error(f"Error registrando interacción: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")



@router.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    status = "healthy" if personalizacion_service else "degraded"
    return {
        "status": status,
        "service": "microservicio_personalizacion",
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Microservicio de Personalización funcionando",
        "version": "1.0.0",
        "fastapi_version": "0.120.4",
        "status": "ready",
        "endpoints": [
            "/CrearPreferencia",
            "/RecibirOntologia",
            "/NotificarSalidaDeUsuario",
            "/RegistroInteraccionUsuarioObjeto",
            "/health",
            "/docs"
        ]
    }