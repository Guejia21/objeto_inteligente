"""
    @file personalizacion_controller.py
    @brief Controlador REST para gestión de preferencias e interacciones de usuario.
    @details
    Proporciona endpoints para:
    - Crear preferencias/contratos ECA para usuario
    - Recibir y cargar ontologías de perfil de usuario
    - Notificar salida de usuario (desactivar ECAs)
    - Registrar interacciones usuario-objeto
    - Health check del servicio
    
    @note El microservicio integra con micro_gestion_conocimiento y micro_automatizacion.
    
    @author  NexTech
    @version 1.0
    @date 2025-01-10
    
    @see PersonalizacionService Para lógica de negocio
    @see micro_gestion_conocimiento Para ontologías
    @see micro_automatizacion Para ECAs
"""

from fastapi import APIRouter, Depends, HTTPException, Query, File, Form, UploadFile
import json
from application.dtos.request_dtos import CrearPreferenciaRequest, MakeContractRequest, RegistroInteraccionDTO
from domain.services.personalizacion_service import PersonalizacionService
from infrastructure.logging.Logging import logger
from deps import get_personalizacion_service



router = APIRouter(prefix="/personalizacion", tags=["Gestión de Personalización de Usuario"])
"""@var router Router principal para endpoints de personalización."""

@router.post("/CrearPreferencia")
async def crear_preferencia(
    data:MakeContractRequest,
    personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)
):
    """
        @brief Crea una nueva preferencia/contrato ECA para el usuario actual.
        
        @param data DTO MakeContractRequest con definición del contrato ECA.
        @param personalizacion_service Servicio de personalización (inyectado).
        
        @return JSONResponse con status 200 si exitoso, o error 400/500.
        
        @exception HTTPException Si email no coincide o hay error en micro_automatizacion.
        
        @details
        Crea una regla ECA (contrato) que automatiza comportamientos del usuario.
        
        Flujo:
        1. Verifica que el email del DTO coincida con el usuario actual
        2. Envía solicitud al microservicio micro_automatizacion
        3. Registra la preferencia en ontología de usuario
        
        @see PersonalizacionService.crear_preferencia()
        @see micro_automatizacion Para implementación de ECAs
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
    file: UploadFile = File(..., description="Archivo de ontología (.owl)"),
    nombre: str = Form(..., description="Nombre de la ontología"),
    ipCoordinador: str = Form(..., description="IP del coordinador"),
    personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)
):
    """
        @brief Recibe y carga ontología de perfil de usuario.
        
        @param file Archivo .owl con ontología del usuario.
        @param nombre Identificador de la ontología.
        @param ipCoordinador IP del coordinador (para tracking/notificación).
        @param personalizacion_service Servicio de personalización.
        
        @return JSONResponse con status 200 si exitoso, o error 400/500.
        
        @exception HTTPException Si hay error en procesamiento o envío.
        
        @details
        Endpoint de integración: recibe ontología del coordinador y la envía
        al microservicio micro_gestion_conocimiento para población.
        
        Flujo:
        1. Valida que el archivo sea .owl
        2. Envía al microservicio de ontologías
        3. Guarda IP del coordinador para tracking
        4. Activa ECAs del usuario
        
        @see PersonalizacionService.recibir_ontologia()
        @see micro_gestion_conocimiento Para carga de ontologías
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
        @brief Notifica la salida del usuario y desactiva sus ECAs.
        
        @param personalizacion_service Servicio de personalización.
        
        @return JSONResponse con status 200 si exitoso, o error 500.
        
        @exception HTTPException Si hay error coordinando desactivación.
        
        @details
        Implementa HU-2 (Historia de Usuario 2): cuando el usuario se desconecta,
        desactiva todas sus reglas ECAs en el microservicio de automatización.
        
        @note Operación de coordinación inter-servicios.
        
        @see PersonalizacionService.desactivarEcasUsuarioActual()
        @see micro_automatizacion Para desactivación de ECAs
    """
    try:        
        return personalizacion_service.desactivarEcasUsuarioActual()
    except Exception as e:
        logger.error(f" Error notificando salida de usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/RegistroInteraccionUsuarioObjeto")
async def registro_interaccion_usuario_objeto(data: RegistroInteraccionDTO, personalizacion_service: PersonalizacionService = Depends(get_personalizacion_service)):
    """
        @brief Registra una interacción entre usuario y objeto inteligente.
        
        @param data DTO RegistroInteraccionDTO con evento de interacción.
        @param personalizacion_service Servicio de personalización.
        
        @return JSONResponse con status 200 si exitoso, o error 500.
        
        @exception HTTPException Si hay error al registrar interacción.
        
        @details
        Registra eventos de interacción (p. ej. usuario accede a objeto,
        modifica preferencias, etc.) para crear historial y base para
        personalización e inferencia de patrones.
        
        @see PersonalizacionService.registroInteraccionUsuarioObjeto()
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
    """
        @brief Health check / status del microservicio.
        
        @param personalizacion_service Servicio de personalización.
        
        @return JSON con status: 'healthy' o 'degraded', nombre y versión del servicio.
        
        @details
        Endpoint para monitoreo y orquestación de contenedores.
        Verifica que el servicio esté disponible.
    """
    status = "healthy" if personalizacion_service else "degraded"
    return {
        "status": status,
        "service": "microservicio_personalizacion",
        "version": "1.0.0"
    }
