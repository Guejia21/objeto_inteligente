from fastapi import APIRouter, Depends, HTTPException

from application.dtos import ECAResponse, MakeContractRequest
from deps import get_eca_service
from application.eca_service import EcaService

router = APIRouter(prefix="/eca", tags=["ECAs"])

# Crear nueva ECA
@router.post("/makeContract", response_model=ECAResponse, responses={400: {"model": ECAResponse}})
async def crear_eca(eca: MakeContractRequest, service: EcaService = Depends(get_eca_service)):  
    try:
        result = await service.crear_eca(eca)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

"""# Editar ECA existente
@router.put("/", response_model=SuccessResponse)
def editar_eca(eca: EcaCreate):
    try:
        result = service.editar_eca(eca.dict())
        return SuccessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Listar ECAs
@router.get("/", response_model=List[ListEcaResponse])
def listar_ecas():
    try:
        return service.listar_ecas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener ECA por nombre
@router.get("/{name}", response_model=EcaResponse)
def obtener_eca(name: str):
    try:
        return service.obtener_eca(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cambiar estado (on/off)
@router.patch("/state", response_model=SuccessResponse)
def cambiar_estado(request: StateChange):
    try:
        result = service.cambiar_estado(request.name_eca, request.state)
        return SuccessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Eliminar ECA
@router.delete("/{name}", response_model=SuccessResponse)
def eliminar_eca(name: str):
    try:
        result = service.eliminar_eca(name)
        return SuccessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""