from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.domain.eca_models import (
    EventoMedicionDTO,
    AccionResultDTO,
)
from app.application.automatizacion_service import AutomatizacionECAService
from app.deps import get_automatizacion_service

router = APIRouter(
    prefix="/automatizacion/ecas",
    tags=["Automatización ECAs"],
)

# ===========================================================
# 1) PROCESAR EVENTO
# ===========================================================

@router.post("/procesar_evento", response_model=List[AccionResultDTO])
async def procesar_evento(
    evento: EventoMedicionDTO,
    service: AutomatizacionECAService = Depends(get_automatizacion_service),
):
    """
    Dado un evento (osid, datastream, valor), evalúa todas las ECAs
    y retorna las acciones que deben ejecutarse.
    """
    try:
        return await service.procesar_evento(evento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================================================
# 2) SEND COMMAND
# ===========================================================

@router.post("/send_command")
async def send_command(osid_destino: str, recurso: str, valor: str):
    """
    Envía un comando hacia un objeto inteligente (solo genera el JSON, no comunica hardware)
    """
    comando = {
        "status": "comando_enviado",
        "osid_destino": osid_destino,
        "recurso": recurso,
        "valor": valor
    }

    return comando

# ===========================================================
# 3) ENCENDER / APAGAR ECA
# ===========================================================

@router.put("/set_eca_state")
async def set_eca_state(
    nombre_eca: str,
    nuevo_estado: str,
    service: AutomatizacionECAService = Depends(get_automatizacion_service),
):
    """
    Activa o desactiva un ECA específico.
    """
    try:
        return await service.set_eca_state(nombre_eca, nuevo_estado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================================================
# 4) LISTAR ECAS
# ===========================================================

@router.get("/listar")
async def listar_ecas(
    osid: str,
    service: AutomatizacionECAService = Depends(get_automatizacion_service),
):
    """
    Lista todas las ECAs asociadas a un objeto.
    """
    try:
        return await service.list_ecas(osid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================================================
# 5) DESACTIVAR TODAS LAS ECAS DE UN OBJETO
# ===========================================================

@router.put("/disable_all")
async def disable_all_ecas(
    osid: str,
    service: AutomatizacionECAService = Depends(get_automatizacion_service),
):
    """
    Desactiva todas las ECAs de un objeto.
    """
    try:
        return await service.disable_all_ecas(osid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
