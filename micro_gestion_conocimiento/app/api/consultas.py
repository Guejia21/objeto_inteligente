
from app.application.consultas_service import ConsultasService
from fastapi import APIRouter, Depends

from app.deps import get_consultas_service

router = APIRouter()
@router.get("/consultar_id", response_model=str)
async def consultar_id(service: ConsultasService = Depends(get_consultas_service)) -> str:
    """Endpoint para consultar el ID del objeto inteligente."""
    return service.consultar_id()