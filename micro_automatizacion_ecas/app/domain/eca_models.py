from pydantic import BaseModel
from typing import Optional, List, Literal


class EcaDTO(BaseModel):
    # Datos de la ECA (Dinamic)
    name_eca: str
    state_eca: str
    user_eca: Optional[str] = "default"
    interest_entity_eca: Optional[str] = None

    # Evento (Event)
    id_event_object: str
    ip_event_object: str
    id_event_resource: str
    name_event_resource: str
    name_event_object: str

    # Condición (Condition)
    comparator_condition: Literal["mayor", "menor", "igual", "mayor_igual", "menor_igual", "distinto", "==", "!=", ">", "<", ">=", "<="]
    meaning_condition: str
    type_variable_condition: Literal["int", "float", "string", "bool"]
    unit_condition: Optional[str] = None
    variable_condition: str  # ej: valor del datastream

    # Acción (Action)
    comparator_action: Optional[str] = None
    id_action_resource: str
    id_action_object: str
    ip_action_object: str
    meaning_action: str
    name_action_object: str
    name_action_resource: str
    type_variable_action: Literal["int", "float", "string", "bool"]
    unit_action: Optional[str] = None
    variable_action: str


class EventoMedicionDTO(BaseModel):
    """
    Evento que dispara la evaluación de ECAs.
    - osid: id del objeto inteligente
    - datastream_id: recurso que generó la medición
    - valor: valor medido (numérico o string)
    - user_eca: opcional, para filtrar reglas por usuario
    """
    osid: str
    datastream_id: str
    valor: str  # lo manejamos como string y luego se castea según type_variable_condition
    user_eca: Optional[str] = None


class AccionResultDTO(BaseModel):
    """
    Resultado de la evaluación de ECAs:
    Acciones que se deberían ejecutar.
    """
    name_eca: str
    osid_object_action: str
    ip_action_object: str
    id_action_resource: str
    name_action_resource: str
    variable_action: str
    type_variable_action: str
    meaning_action: str
    unit_action: Optional[str] = None
