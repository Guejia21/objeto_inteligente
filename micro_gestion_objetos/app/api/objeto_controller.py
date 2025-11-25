
from fastapi import APIRouter, Depends, Query,HTTPException

from application.objeto_service import ObjetoService
from deps import get_objeto_service
from application.dtos import ObjectData


router = APIRouter(prefix="/objeto", tags=["Gestión de objeto inteligente"])

@router.get("/Identificator")
async def get_identificator(osid: str = Query(..., description="ID del objeto inteligente"), objeto_service: ObjetoService = Depends(get_objeto_service)):
    """Obtiene los metadatos del objeto inteligente dado su osid."""
    try:
        return await objeto_service.getIdentificator(osid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

#TODO: Definir schema para el JSON de entrada
@router.post("/StartObject")
async def start_object(data: ObjectData, objeto_service: ObjetoService = Depends(get_objeto_service)):
    """Inicia el objeto inteligente con los datos proporcionados."""
    try:
        return await objeto_service.startObject(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/SendState")
async def get_state(osid: str = Query(..., description="ID del objeto inteligente"), objeto_service: ObjetoService = Depends(get_objeto_service)):
    """Obtiene el estado actual de los datastreams del objeto inteligente dado su osid."""
    try:
        return await objeto_service.get_state(osid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/SendData")
async def send_data(
    osid: str = Query(..., description="ID del objeto inteligente"),
    variableEstado: bool = Query(..., description="Variable del estado"),
    tipove: str = Query(..., description="Tipo de variable (act, sen, etc.)"),
    objeto_service: ObjetoService = Depends(get_objeto_service)
):   
    """Envía datos al objeto inteligente."""
    try:
        return await objeto_service.send_data(osid, variableEstado, tipove)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/SendServiceState")
async def send_service_state(osid: str = Query(..., description="ID del objeto inteligente"),objeto_service: ObjetoService = Depends(get_objeto_service)):
    """Envía el estado de los servicios del objeto inteligente dado su osid."""
    try:
        return await objeto_service.send_service_state(osid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/SendCommand")
async def send_command(osid: str = Query(..., description="ID del objeto origen"),osidDestino: str = Query(..., description="ID del objeto destino"),comando: str = Query(..., description="Comando a ejecutar"),
    objeto_service: ObjetoService = Depends(get_objeto_service)
):
    """Envía un comando desde un objeto inteligente a otro."""
    params = {"osid": osid, "osidDestino": osidDestino, "comando": comando}
    try:
         return await objeto_service.send_command(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
