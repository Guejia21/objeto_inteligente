from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, Dict, Any
from datetime import datetime

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

class ECAResponse(BaseModel):
    """Respuesta de operaciones con ECA"""
    status: Literal["success", "error"]
    code: str
    message: str
    data: Optional[Dict[str, Any]] = None

class SendDataResponse(BaseModel):
    """Respuesta de SendData"""
    osid: str
    datastream_id: str
    datastream_format: str
    value: str
    timestamp: Optional[str] = None
class CommandActionData(BaseModel):
    """
    Datos del comando/acción a ejecutar.
    
    Este schema representa el contenido del XML "comando"
    pero en formato JSON para la migración.
    """
    id_action_resource: str = Field(..., description="ID del datastream/actuador a controlar")
    comparator_action: str = Field(..., description="Comparador: igual, mayor, menor, incrementar, decrementar")
    variable_action: str = Field(..., description="Valor a establecer")
    type_variable_action: str = Field(..., description="Tipo del valor: string, float, int, bool")
    
    # Campos opcionales
    name_action_object: Optional[str] = Field(None, description="Nombre del objeto acción")
    name_action_resource: Optional[str] = Field(None, description="Nombre del recurso")
    unit_action: Optional[str] = Field(None, description="Unidad de la acción")
    meaning_action: Optional[str] = Field(None, description="Significado: turn_on, turn_off, set_value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_action_resource": "ventilador",
                "comparator_action": "igual",
                "variable_action": "on",
                "type_variable_action": "string",
                "name_action_object": "Actuador Ventilador",
                "name_action_resource": "Ventilador",
                "unit_action": "state",
                "meaning_action": "turn_on"
            }
        }
class SendCommandRequest(BaseModel):
    """
    Schema completo para SendCommand en formato JSON
    (para migración del sistema XML a JSON)
    """
    osid: str = Field(..., description="ID del objeto origen (quien envía el comando)")
    osidDestino: str = Field(..., description="ID del objeto destino (quien ejecuta)")
    comando: CommandActionData = Field(..., description="Datos del comando a ejecutar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "osid": "ESP32_Sala",
                "osidDestino": "ESP32_Cocina",
                "comando": {
                    "id_action_resource": "ventilador",
                    "comparator_action": "igual",
                    "variable_action": "on",
                    "type_variable_action": "string"
                }
            }
        }
class ECAStateRequest(BaseModel):
    """Petición para cambiar el estado de un ECA"""
    osid: str = Field(..., description="ID del objeto que recibe la petición")
    nombreECA: str = Field(..., description="Nombre del ECA a modificar")
    userECA: str = Field(..., description="Email del usuario creador del ECA")
    comando: Literal["on", "off"] = Field(..., description="Nuevo estado del ECA")
    
    class Config:
        json_schema_extra = {
            "example": {
                "osid": "708637323",
                "nombreECA": "Temperatura_Led",
                "userECA": "usuario@example.com",
                "comando": "on"
            }
        }