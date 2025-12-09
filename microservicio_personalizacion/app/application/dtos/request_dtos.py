from pydantic import BaseModel, Field
from typing import Dict, Any, Literal, Optional

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
class RegistroInteraccionDTO(BaseModel):
    mac:str = Field(..., description="MAC del usuario")
    idUsuario:str = Field(..., description="ID del usuario")
    accion:Literal["CARGAR","ELIMINAR"] = Field(..., description="Acción realizada")
    email: str = Field(..., description="Correo electrónico del usuario")
    idDataStream: str = Field(..., description="ID del datastream")
    comando: str = Field(..., description="Comando ejecutado")
    osid: str = Field(..., description="ID del objeto inteligente")
    dateInteraction: str = Field(..., description="Fecha y hora de la interacción")
    class Config:
        json_schema_extra = {
            "example": {
                "mac": "00:1A:7D:DA:71:13",
                "idUsuario": "user_123",
                "accion": "CARGAR",
                "email": "usuario@example.com",
                "idDataStream": "relay",
                "comando": "on",
                "osid": "ESP32_Sala",
                "dateInteraction": "15/09/23 14:30:00"
                }
        }
class VariableValue(BaseModel):
    """Representa una variable con su valor y tipo"""
    value: str
    type: str = Field(..., description="float, int, string, bool")
class EventData(BaseModel):
    """Datos del evento que dispara el ECA"""
    id_event_object: str = Field(..., description="ID del objeto que genera el evento")
    ip_event_object: str = Field(..., description="IP del objeto evento")
    name_event_object: str = Field(..., description="Nombre del objeto evento")
    id_event_resource: str = Field(..., description="ID del datastream/recurso")
    name_event_resource: str = Field(..., description="Nombre del recurso")

class ConditionData(BaseModel):
    """Condición que debe cumplirse para ejecutar la acción"""
    comparator_condition: str = Field(..., description="mayor, menor, igual, mayor_igual, menor_igual, diferente")
    meaning_condition: str = Field(..., description="threshold, range, etc.")
    unit_condition: str = Field(..., description="Unidad de medida: C, %, lux, etc.")
    variable_condition: VariableValue = Field(..., description="Valor a comparar")

class ActionData(BaseModel):
    """Acción a ejecutar cuando se cumpla la condición"""
    id_action_object: str = Field(..., description="ID del objeto que ejecuta la acción")
    ip_action_object: str = Field(..., description="IP del objeto acción")
    name_action_object: str = Field(..., description="Nombre del objeto acción")
    id_action_resource: str = Field(..., description="ID del datastream/actuador")
    name_action_resource: str = Field(..., description="Nombre del recurso")
    comparator_action: str = Field(..., description="igual, incrementar, decrementar")
    unit_action: str = Field(..., description="Unidad de la acción")
    meaning_action: str = Field(..., description="turn_on, turn_off, set_value")
    variable_action: VariableValue = Field(..., description="Valor a establecer")

class ECAContract(BaseModel):
    """Contrato ECA completo"""
    name_eca: str = Field(..., description="Nombre único del ECA")
    state_eca: Literal["on", "off"] = Field(default="on", description="Estado del ECA")
    eca_state: Literal["active", "inactive"] = Field(default="active", description="Estado de ejecución")
    interest_entity_eca: str = Field(..., description="Entidad de interés: Ambiente, Usuario, etc.")
    user_eca: Optional[str] = Field(None, description="Email del usuario creador")
    
    event: EventData
    condition: ConditionData
    action: ActionData
    
    class Config:
        json_schema_extra = {
            "example": {
                "name_eca": "Temperatura_Led",
                "state_eca": "on",
                "eca_state": "active",
                "interest_entity_eca": "Ambiente",
                "user_eca": "usuario@example.com",
                "event": {
                    "id_event_object": "708637323",
                    "ip_event_object": "192.168.8.208",
                    "name_event_object": "Sensor Temperatura",
                    "id_event_resource": "temperatura",
                    "name_event_resource": "Temperatura"
                },
                "condition": {
                    "comparator_condition": "mayor",
                    "meaning_condition": "threshold",
                    "unit_condition": "C",
                    "variable_condition": {
                        "value": "30.5",
                        "type": "float"
                    }
                },
                "action": {
                    "id_action_object": "708637323",
                    "ip_action_object": "192.168.8.208",
                    "name_action_object": "Actuador Ventilador",
                    "id_action_resource": "relay",
                    "name_action_resource": "Ventilador",
                    "comparator_action": "igual",
                    "unit_action": "state",
                    "meaning_action": "turn_on",
                    "variable_action": {
                        "value": "on",
                        "type": "bool"
                    }
                }
            }
        }

class MakeContractRequest(BaseModel):
    """Petición para crear un contrato ECA"""
    osid: str = Field(..., description="ID del objeto que recibe el contrato")
    osidDestino: str = Field(..., description="ID del objeto destino/acción")
    email: str = Field(..., description="Email del usuario creador")
    contrato: ECAContract = Field(..., description="Contrato ECA en formato JSON")
    
    class Config:
        json_schema_extra = {
            "example": {
                "osid": "708637323",
                "osidDestino": "708637323",
                "email": "usuario@example.com",
                "contrato": ECAContract.Config.json_schema_extra["example"]
            }
        }

