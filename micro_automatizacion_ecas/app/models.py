from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class EcaBase(BaseModel):
    """Modelo base para contratos ECA"""
    osid_origen: str
    osid_destino: str
    evento: str 
    accion: str
    condiciones: Optional[Dict[str, Any]] = None
    user_eca: Optional[str] = None

class EcaCreate(EcaBase):
    """Modelo para crear un contrato"""
    name_eca: str
    state_eca: str = "off"
    id_event_resource: str
    id_action_resource: str
    comparator_action: str
    variable_action: str
    type_variable_action: str

class EcaResponse(EcaBase):
    """Modelo de respuesta para contratos"""
    id_contrato: str
    estado: str
    name_eca: str



class StateChange(BaseModel):
    """Modelo para cambiar estado de ECAs"""
    state: str = Field(..., pattern="^(on|off)$")
    nombreECA: str

class ListEcaResponse(BaseModel):
    """Modelo para listar ECAs"""
    name_eca: str
    state_eca: str
    user_eca: Optional[str] = None
    id_event_object: str
    id_action_object: str
    id_event_resource: str
    id_action_resource: str
    comparator_action: str
    variable_action: str
    type_variable_action: str

class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    detail: str
    code: str

class SuccessResponse(BaseModel):
    """Modelo para respuestas exitosas"""
    message: str
    code: str = "1000"  # código exitoso basado en CodigosRespuestas.exitoso

class StopAllRequest(BaseModel):
    """Modelo para apagar todos los ECAs"""
    osid: str
    comando: str = "off"