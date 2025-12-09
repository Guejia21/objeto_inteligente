from fastapi import APIRouter, Depends, HTTPException, Query, File, Form, UploadFile
import json
from application.dtos.request_dtos import CrearPreferenciaRequest, MakeContractRequest, RegistroInteraccionDTO
from domain.services.personalizacion_service import PersonalizacionService
from infrastructure.logging.Logging import logger
from deps import get_personalizacion_service



router = APIRouter(prefix="/personalizacion", tags=["Gestión de Personalización de Usuario"])

@router.post("/CrearPreferencia")
async def crear_preferencia(
    data:MakeContractRequest,
    personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)
):
    """    
    Crea una nueva preferencia ECA para el usuario actual
    """
    try:
        return await personalizacion_service.crear_preferencia(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en CrearPreferencia: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/RecibirOntologia")
async def recibir_ontologia(
    file: UploadFile = File(..., description="Archivo de ontología (.owl)"),    nombre: str = Form(..., description="Nombre de la ontología"),
    ipCoordinador: str = Form(..., description="IP del coordinador"),
    personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)
):
    """
    ENDPOINT DE PERSONALIZACIÓN - Recibe ontología y la envía al microservicio de ontologías
    """
    try:
        return await personalizacion_service.recibir_ontologia(file,nombre,ipCoordinador)            
    except Exception as e:
        logger.error(f" Error procesando ontología: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/NotificarSalidaDeUsuario")
async def notificar_salida_usuario(    
    personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)
):
    """
     ENDPOINT DE PERSONALIZACIÓN - HU-2: Notificación de salida de usuario
    Coordina con el microservicio de automatización para desactivar ECAs
    """
    try:        
        return personalizacion_service.desactivarEcasUsuarioActual()
    except Exception as e:
        logger.error(f" Error notificando salida de usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/RegistroInteraccionUsuarioObjeto")
async def registro_interaccion_usuario_objeto(data: RegistroInteraccionDTO, personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)):
    """
    Registra interacciones entre usuarios y objetos
    """
    try:                
        return personalizacion_service.registroInteraccionUsuarioObjeto(data)    
    except Exception as e:
        logger.error(f"Error registrando interacción: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/health")
async def health_check(
    personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)
):
    """Endpoint de health check para monitoreo"""
    status = "healthy" if personalizacion_service else "degraded"
    return {
        "status": status,
        "service": "microservicio_personalizacion",
        "version": "1.0.0"
    }
