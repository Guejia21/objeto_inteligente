
from fastapi import APIRouter, Depends, Query

from app.application import ObjetoService
from app.deps import get_objeto_service


router = APIRouter(prefix="/objeto", tags=["Gestión de objeto inteligente"])

@router.get("/Identificator")
def get_identificator(osid: int = Query(..., gt=0, description="ID del objeto inteligente"), objeto_service: ObjetoService = Depends(get_objeto_service)):
    return objeto_service.getIdentificator(osid)

#TODO: Definir schema para el JSON de entrada
@router.post("/StartObject")
def start_object(json_data: dict, objeto_service: ObjetoService = Depends(get_objeto_service)):
    return objeto_service.startObject(json_data)