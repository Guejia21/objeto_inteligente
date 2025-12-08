from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from application.dtos import ECAResponse, ECAStateRequest, MakeContractRequest
from deps import get_eca_service
from application.eca_service import EcaService
from application.dtos import SendCommandRequest



router = APIRouter(prefix="/eca", tags=["ECAs"])

# Crear nueva ECA
@router.post("/")
async def crear_eca(eca: MakeContractRequest, service: EcaService = Depends(get_eca_service)):  
    """Crear una nueva regla ECA."""
    try:
        result = await service.crear_eca(eca)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/")
async def listar_ecas(osid: str = Query(..., description="ID del objeto inteligente"),service: EcaService = Depends(get_eca_service)):
    """Listar todas las ECAs del objeto inteligente."""
    try:
        return await service.listar_ecas(osid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.patch("/")
async def apagar_ecas(osid: str = Query(..., description="ID del objeto inteligente"),service: EcaService = Depends(get_eca_service)):
    """Apagar todas las ECAs del objeto inteligente."""
    try:
        return await service.apagar_ecas(osid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/")
async def eliminar_eca(
    osid:str=Query(..., description="ID del objeto inteligente"),
    eca_name: str = Query(..., description="Nombre del ECA a eliminar"),
    user_eca: str = Query(..., description="Usuario dueño del ECA"), 
    service: EcaService = Depends(get_eca_service)):
    try:         
        return await service.eliminar_eca(osid,eca_name, user_eca)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.put("/state")
async def cambiar_estado(request: ECAStateRequest, service: EcaService = Depends(get_eca_service)):
    try:
        return await service.cambiar_estado_eca(request)        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.put("/edit")
async def editar_eca(eca: MakeContractRequest, service: EcaService = Depends(get_eca_service)):
    try:
        return await service.editar_eca(eca)        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/send_command")
async def send_command(request: SendCommandRequest, service: EcaService = Depends(get_eca_service)):
    """Envía un comando a un datastream actuador si existe un contrato."""
    try:
        return await service.send_command(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
