from pydantic import BaseModel
from typing import Dict, Any, Optional

class CrearPreferenciaRequest(BaseModel):
    email: str
    osid: str
    osidDestino: str
    contrato: Dict[str, Any]

class RecibirOntologiaRequest(BaseModel):
    file: bytes
    nombre: str
    ipCoordinador: str

class NotificarSalidaRequest(BaseModel):
    osid: str

class RegistroInteraccionRequest(BaseModel):
    email: str
    idDataStream: str
    comando: str
    osid: str
    mac: str
    dateInteraction: str

class SetEcaStateRequest(BaseModel):
    osid: str
    nombreECA: str
    comando: str  # "on" o "off"

class ListarEcasRequest(BaseModel):
    osid: str

class EliminarEcaRequest(BaseModel):
    osid: str
    ecaName: str
