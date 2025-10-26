
from fastapi import APIRouter, Depends, Query

from app.application.objeto_service import ObjetoService
from app.deps import get_objeto_service
from app.application.dtos import ObjectData


router = APIRouter(prefix="/objeto", tags=["Gestión de objeto inteligente"])

@router.get("/Identificator")
async def get_identificator(osid: int = Query(..., gt=0, description="ID del objeto inteligente"), objeto_service: ObjetoService = Depends(get_objeto_service)):
    """Obtiene los metadatos del objeto inteligente dado su osid."""
    return await objeto_service.getIdentificator(osid)

#TODO: Definir schema para el JSON de entrada
@router.post("/StartObject")
async def start_object(data: ObjectData, objeto_service: ObjetoService = Depends(get_objeto_service)):
    """Inicia el objeto inteligente con los datos proporcionados."""
    return await objeto_service.startObject(data)