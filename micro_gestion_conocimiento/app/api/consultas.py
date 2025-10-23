
from app.application.consultas_service import ConsultasService
from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_consultas_service

router = APIRouter(prefix="/consultas", tags=["Consultas de Base de conocimiento"])
@router.get("/consultar_id", response_model=str)
async def consultar_id(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el ID del objeto inteligente."""
    try:
        return service.consultarId()
    except Exception as e:        
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_description", response_model=str)
async def consultar_description(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la descripción del estado."""
    try:
        return service.consultar_description()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
async def consultar_private(service: ConsultasService = Depends(get_consultas_service)) -> bool:
    """Endpoint para consultar si el feed/objeto es privado."""
    try:
        return service.consultarPrivate()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_title", response_model=str)
async def consultar_title(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el título descriptivo del estado."""
    try:
        return service.consultarTitle()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_feed", response_model=str)
async def consultar_feed(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la URL del feed asociada al estado."""
    try:
        return service.consultarFeed()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_status", response_model=str)
async def consultar_status(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el estado (status) del estado del objeto."""
    try:
        return service.consultarStatus()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_updated", response_model=str)
async def consultar_updated(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la fecha/hora de la última actualización del estado."""
    try:
        return service.consultarUpdated()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_created", response_model=str)
async def consultar_created(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la fecha de creación del estado."""
    try:
        return service.consultarCreated()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_creator", response_model=str)
async def consultar_creator(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el creador del estado/objeto."""
    try:
        return service.consultarCreator()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_version", response_model=str)
async def consultar_version(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la versión asociada al estado."""
    try:
        return service.consultarVersion()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_website", response_model=str)
async def consultar_website(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la URL de un sitio web relevante para el feed/objeto."""
    try:
        return service.consultarWebsite()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/consultar_service_state", response_model=str)
async def consultar_service_state(service: ConsultasService = Depends(get_consultas_service)) ->    str:
    """Endpoint para consultar el estado del servicio básico del objeto."""
    try:
        return service.consultarServiceState()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))