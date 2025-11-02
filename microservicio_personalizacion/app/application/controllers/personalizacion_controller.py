from fastapi import APIRouter, HTTPException, Query, File, Form, UploadFile
from typing import Dict, Any
import json
import logging

from app.application.dtos.request_dtos import (
    CrearPreferenciaRequest,
    RecibirOntologiaRequest,
    NotificarSalidaRequest,
    RegistroInteraccionRequest
)
from app.domain.services.personalizacion_service import PersonalizacionService
from app.infrastructure.repositories.personalizacion_repository_impl import PersonalizacionRepositoryImpl  # ✅ NUEVA IMPORTACIÓN

logger = logging.getLogger(__name__)

# Configurar dependencias
try:
    repository = PersonalizacionRepositoryImpl()  # ✅ Usar la implementación concreta
    personalizacion_service = PersonalizacionService(repository)
    logger.info("✅ Dependencias del servicio de personalización inicializadas correctamente")
except Exception as e:
    logger.error(f"Error inicializando dependencias: {e}")
    personalizacion_service = None

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
        
        logger.info(f"✅ Preferencia creada exitosamente para usuario: {email}")
        return resultado["mensaje"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en CrearPreferencia: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/SetEcaState")
async def set_eca_state(
    osid: str = Query(..., description="ID del objeto"),
    nombreECA: str = Query(..., description="Nombre del ECA"),
    comando: str = Query(..., description="Comando: 'on' o 'off'")
):
    """
    Endpoint para activar/desactivar un ECA específico
    """
    try:
        if not personalizacion_service:
            raise HTTPException(status_code=500, detail="Servicio no disponible")
            
        logger.info(f" SetEcaState recibido - ECA: {nombreECA}, comando: {comando}")
        
        resultado = await personalizacion_service.cambiar_estado_eca(osid, nombreECA, comando)
        
        if resultado["status_code"] != 200:
            raise HTTPException(
                status_code=resultado["status_code"],
                detail=resultado["error"]
            )
        
        logger.info(f"Estado del ECA {nombreECA} cambiado a {comando}")
        return resultado["mensaje"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Error inesperado en SetEcaState: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ... (los demás endpoints mantienen la misma estructura con mejor logging)

@router.post("/RecibirOntologia")
async def recibir_ontologia(
    file: UploadFile = File(..., description="Archivo de ontología (.owl)"),
    nombre: str = Form(..., description="Nombre de la ontología"),
    ipCoordinador: str = Form(..., description="IP del coordinador")
):
    """
    Recibe y procesa una ontología de usuario
    """
    try:
        logger.info(f"Recibiendo ontología: {nombre} desde {ipCoordinador}")
        
        # Leer el contenido del archivo
        file_content = await file.read()
        
        # Lógica para procesar la ontología
        resultado = await personalizacion_service.procesar_ontologia(
            file_content=file_content,
            nombre=nombre,
            ip_coordinador=ipCoordinador
        )
        
        return {"mensaje": "Ontología recibida exitosamente", "status_code": 200, "data": resultado}
    
    except Exception as e:
        logger.error(f"Error procesando ontología: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/NotificarSalidaDeUsuario")
async def notificar_salida_usuario(
    osid: str = Form(..., description="ID del objeto/usuario")
):
    """
    Notifica la salida de un usuario del sistema
    """
    try:
        logger.info(f"Notificando salida de usuario con osid: {osid}")
        
        resultado = await personalizacion_service.desactivar_ecas_por_osid(osid)
        
        return {"mensaje": "Salida de usuario notificada exitosamente", "status_code": 200, "data": resultado}
    
    except Exception as e:
        logger.error(f"Error notificando salida de usuario: {e}")
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
            "/SetEcaState", 
            "/ApagarTodosEcas",
            "/EcaList",
            "/DeleteEca",
            "/RecibirOntologia",
            "/NotificarSalidaDeUsuario",
            "/RegistroInteraccionUsuarioObjeto",
            "/health",
            "/docs"
        ]
    }