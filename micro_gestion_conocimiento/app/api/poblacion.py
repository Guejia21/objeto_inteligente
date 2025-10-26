
from fastapi import APIRouter, Depends, HTTPException
from app.application.dtos import PobladorPayloadDTO
from app.deps import get_poblacion_service
from app.application.poblacion_service import PoblacionService

router = APIRouter(prefix="/poblacion", tags=["Poblacion de Base de conocimiento"])
@router.post("/poblar_metadatos_objeto", response_model=None,status_code=201)
async def poblar_metadatos_objeto(metadata: PobladorPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """Endpoint para poblar los metadatos del objeto inteligente."""
    #TODO si la ontología ya tiene datos del objeto inteligente, no permitir poblarlos de nuevo
    try:
        listaRecursos = [r.model_dump() for r in metadata.dicRec]
        return service.poblar_metadatos_objeto(metadata.dicObj.model_dump(), listaRecursos)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))