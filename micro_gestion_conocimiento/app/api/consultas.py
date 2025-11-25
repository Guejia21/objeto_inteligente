
from application.consultas_service import ConsultasService
from fastapi import APIRouter, Depends, HTTPException

from deps import get_consultas_service
from application.dtos import ECAStateListDTO

ontologia_router = APIRouter(prefix="/ontology/consultas", tags=["Consultas de Base de conocimiento"])
""" Endpoints para consultas sobre la ontología del objeto inteligente."""
@ontologia_router.get("/consultar_active", response_model=bool)
async def consultar_active(service: ConsultasService = Depends(get_consultas_service)) -> bool:
    """Endpoint para consultar si el objeto inteligente está activo."""
    try:
        return service.consultarOntoActiva()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_id", response_model=str)
async def consultar_id(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el ID del objeto inteligente."""
    try:
        return service.consultarId()
    except Exception as e:        
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_description", response_model=str)
async def consultar_description(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la descripción del estado."""
    try:
        return service.consultarDescription()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_private", response_model=bool)
async def consultar_private(service: ConsultasService = Depends(get_consultas_service)) -> bool:
    """Endpoint para consultar si el feed/objeto es privado."""
    try:
        return service.consultarPrivate()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_title", response_model=str)
async def consultar_title(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el título descriptivo del estado."""
    try:
        return service.consultarTitle()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_feed", response_model=str)
async def consultar_feed(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la URL del feed asociada al estado."""
    try:
        return service.consultarFeed()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_status", response_model=str)
async def consultar_status(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el estado (status) del estado del objeto."""
    try:
        return service.consultarStatus()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_updated", response_model=str)
async def consultar_updated(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la fecha/hora de la última actualización del estado."""
    try:
        return service.consultarUpdated()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_created", response_model=str)
async def consultar_created(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la fecha de creación del estado."""
    try:
        return service.consultarCreated()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_creator", response_model=str)
async def consultar_creator(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el creador del estado/objeto."""
    try:
        return service.consultarCreator()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_version", response_model=str)
async def consultar_version(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la versión asociada al estado."""
    try:
        return service.consultarVersion()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_website", response_model=str)
async def consultar_website(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar la URL de un sitio web relevante para el feed/objeto."""
    try:
        return service.consultarWebsite()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.get("/consultar_service_state", response_model=str)
async def consultar_service_state(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el estado del servicio básico del objeto."""
    try:
        return service.consultarServiceState()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@ontologia_router.post("/set_eca_state")
async def set_eca_state(valorNuevo: str, nombreECA: str, service: ConsultasService = Depends(get_consultas_service)):
    """Endpoint para actualizar el estado de una ECA."""
    # Para actualizar correctamente el estado del eca debe enviarse el nombre del eca+nombre del usuario
    try:
        return service.setEcaState(valorNuevo, nombreECA)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@ontologia_router.get("/listar_ecas", response_model=list)
async def listar_ecas(service: ConsultasService = Depends(get_consultas_service)) -> list:
    """Endpoint para listar las ECAs definidas en la ontología."""
    try:
        return service.listarECAs()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@ontologia_router.delete("/eliminar_eca")
async def eliminar_eca(nombreECA: str, service: ConsultasService = Depends(get_consultas_service)):
    """Endpoint para eliminar una ECA de la ontología."""
    try:
        return service.eliminarECA(nombreECA)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@ontologia_router.get("/listar_dinamic_estado", response_model=list)
async def listar_dinamic_estado(eca_state: str, service: ConsultasService = Depends(get_consultas_service)) -> list:
    """Endpoint para listar las ECAs con un estado específico."""
    try:
        return service.listarDinamicEstado(eca_state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@ontologia_router.patch("/set_eca_list_state")
async def set_eca_list_state(listaEcas: ECAStateListDTO, service: ConsultasService = Depends(get_consultas_service)):
    """Endpoint para actualizar el estado de una lista de ECAs."""
    try:
        return service.setEcaListState(listaEcas.ecas)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

ontologia_usuario_router = APIRouter(prefix="/ontology/consultas_usuario", tags=["Consultas de Usuario"])
""" Endpoints para consultas sobre la ontología del perfil de usuario."""