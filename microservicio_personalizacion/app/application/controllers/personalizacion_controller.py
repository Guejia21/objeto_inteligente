from fastapi import APIRouter, HTTPException, Query
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