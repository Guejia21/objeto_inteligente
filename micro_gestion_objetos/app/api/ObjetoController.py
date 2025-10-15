
from fastapi import APIRouter, Query


router = APIRouter(prefix="/objeto", tags=["Gestión de objeto inteligente"])

@router.get("/identificator")
def get_identificator(osid: int = Query(..., gt=0, description="ID del objeto inteligente")):
    return {"osid": osid}