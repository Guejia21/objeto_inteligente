
from fastapi import APIRouter, Depends, HTTPException
from app.application.dtos import PobladorPayloadDTO
from app.deps import get_poblacion_service
from app.application.poblacion_service import PoblacionService
router = APIRouter()
@router.post("/poblar_metadatos_objeto", response_model=None)
async def poblar_metadatos_objeto(metadata: PobladorPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """Endpoint para poblar los metadatos del objeto inteligente."""
    try:
        listaRecursos = [r.model_dump() for r in metadata.dicRec]
        return service.poblar_metadatos_objeto(metadata.dicObj.model_dump(), listaRecursos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))