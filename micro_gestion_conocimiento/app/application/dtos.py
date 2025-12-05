from typing import List, Literal, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ObjectMetadata(BaseModel):
    id: str = Field(..., json_schema_extra={"description": "Identificador del objeto inteligente", "example": "objeto_123"})
    ip_object: Optional[str] = Field(None, json_schema_extra={"description": "Dirección IP del objeto inteligente", "example": "192.168.1.1"})
    version: Optional[str] = Field(None, json_schema_extra={"description": "Versión del objeto inteligente", "example": "1.0"})
    creator: Optional[str] = Field(None, json_schema_extra={"description": "Creador del objeto inteligente", "example": "Juan Perez"})
    status: Optional[int] = Field(None, json_schema_extra={"description": "Estado del objeto inteligente", "example": 1})
    tags: List[str] = Field(default_factory=list, json_schema_extra={"description": "Etiquetas del objeto inteligente", "example": ["tag1", "tag2"]})
    title: Optional[str] = Field(None, json_schema_extra={"description": "Título del objeto inteligente", "example": "Título del objeto"})
    private: Optional[bool] = Field(None, json_schema_extra={"description": "Indica si el objeto inteligente es privado", "example": True})
    description: Optional[str] = Field(None, json_schema_extra={"description": "Descripción del objeto inteligente", "example": "Descripción del objeto"})
    updated: Optional[str] = Field(None, json_schema_extra={"description": "Fecha de actualización del objeto inteligente", "example": "2022-01-01"})
    website: Optional[str] = Field(None, json_schema_extra={"description": "Sitio web del objeto inteligente", "example": "https://ejemplo.com"})
    feed: Optional[str] = Field(None, json_schema_extra={"description": "Feed del objeto inteligente", "example": "https://ejemplo.com/feed"})
    created: Optional[str] = Field(None, json_schema_extra={"description": "Fecha de creación del objeto inteligente", "example": "2022-01-01"})

    # Campos usados por poblarLocation (en tu código pasan el mismo diccionario)
    name: Optional[str] = Field(None, json_schema_extra={"description": "Nombre de la ubicación", "example": "Oficina"})
    domain: Optional[int] = Field(None, json_schema_extra={"description": "Dominio de la ubicación", "example": 1})
    lat: Optional[float] = Field(None, json_schema_extra={"description": "Latitud de la ubicación", "example": 19.4326})
    lon: Optional[float] = Field(None, json_schema_extra={"description": "Longitud de la ubicación", "example": -99.1332})
    ele: Optional[float] = Field(None, json_schema_extra={"description": "Elevación de la ubicación", "example": 2240})

    @field_validator("tags", mode="before")
    def ensure_tags_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)


class DataStream(BaseModel):
    datastream_id: str = Field(..., json_schema_extra={"description": "Identificador del datastream", "example": "temperature_stream"})
    datastream_format: Optional[str] = Field(None, json_schema_extra={"description": "Formato del datastream", "example": "float"})
    feedid: Optional[Any] = Field(None, json_schema_extra={"description": "Identificador del feed", "example": "feed_123"})
    current_value: Optional[Any] = Field(None, json_schema_extra={"description": "Valor actual del datastream", "example": 25.0})
    at: Optional[str] = Field(None, json_schema_extra={"description": "Timestamp del datastream", "example": "2022-01-01T00:00:00Z"})
    max_value: Optional[Any] = Field(None, json_schema_extra={"description": "Valor máximo del datastream", "example": 30.0})
    min_value: Optional[Any] = Field(None, json_schema_extra={"description": "Valor mínimo del datastream", "example": 20.0})
    tags: List[str] = Field(default_factory=list, json_schema_extra={"description": "Etiquetas del datastream", "example": ["temperature", "indoor"]}   )
    datapoints: Optional[Any] = None
    symbol: Optional[str] = None
    label: Optional[str] = None
    unitType: Optional[int] = None
    datastream_type: Optional[str] = None
    featureofinterest: Optional[str] = None
    entityofinterest: Optional[str] = None

    @field_validator("tags", mode="before")
    def ensure_ds_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)


class PobladorPayloadDTO(BaseModel):    
    dicObj: ObjectMetadata = Field(..., description="Diccionario con metadatos del objeto")
    dicRec: List[DataStream] = Field(..., description="Lista de datastreams (recursos)")

    @field_validator("dicRec", mode="before")
    def ensure_list_dicrec(cls, v):
        if v is None:
            return []
        return list(v)
    
class EcaPayloadDTO(BaseModel):    
    """
    Schema para el diccionario ECA aplanado
    Define los atributos necesarios para poblar una regla ECA en la ontología OOS.    
    """
    
    # General ECA attributes
    name_eca: str = Field(..., description="Nombre único del ECA")
    state_eca: Literal["on", "off"] = Field(..., description="Estado del ECA (on/off)")     
    interest_entity_eca: str = Field(..., description="Entidad de interés")
    user_eca: Optional[str] = Field(None, description="Email del usuario creador")
    
    # Event attributes (objeto y recurso que dispara el ECA)
    id_event_object: str = Field(..., description="ID del objeto evento")
    ip_event_object: str = Field(..., description="IP del objeto evento")
    name_event_object: str = Field(..., description="Nombre del objeto evento")
    id_event_resource: str = Field(..., description="ID del datastream evento")
    name_event_resource: str = Field(..., description="Nombre del recurso evento")
    
    # Condition attributes
    comparator_condition: str = Field(
        ..., 
        description="Comparador: mayor, menor, igual, mayor_igual, menor_igual, diferente"
    )
    meaning_condition: str = Field(..., description="Significado de la condición")
    unit_condition: str = Field(..., description="Unidad de medida")
    variable_condition: str = Field(..., description="Valor a comparar (como string)")
    type_variable_condition: str = Field(
        ..., 
        description="Tipo de dato: float, int, string, bool"
    )
    
    # Action attributes (objeto y recurso que ejecuta la acción)
    id_action_object: str = Field(..., description="ID del objeto acción")
    ip_action_object: str = Field(..., description="IP del objeto acción")
    name_action_object: str = Field(..., description="Nombre del objeto acción")
    id_action_resource: str = Field(..., description="ID del datastream/actuador")
    name_action_resource: str = Field(..., description="Nombre del recurso acción")
    comparator_action: str = Field(
        ..., 
        description="Comparador de acción: igual, incrementar, decrementar"
    )
    unit_action: str = Field(..., description="Unidad de la acción")
    meaning_action: str = Field(..., description="Significado de la acción")
    variable_action: str = Field(..., description="Valor de la acción (como string)")
    type_variable_action: str = Field(
        ..., 
        description="Tipo de dato de la acción: float, int, string, bool"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name_eca": "ECA_Temperatura_Ventilador",
                "state_eca": "on",
                "eca_state": "active",
                "interest_entity_eca": "Ambiente",
                "user_eca": "usuario@example.com",
                "id_event_object": "ESP32_Sala",
                "ip_event_object": "192.168.1.10",
                "name_event_object": "Sensor Temperatura Sala",
                "id_event_resource": "temperatura",
                "name_event_resource": "Temperatura",
                "comparator_condition": "mayor",
                "meaning_condition": "threshold",
                "unit_condition": "C",
                "variable_condition": "30.5",
                "type_variable_condition": "float",
                "id_action_object": "ESP32_Cocina",
                "ip_action_object": "192.168.1.11",
                "name_action_object": "Actuador Ventilador",
                "id_action_resource": "ventilador",
                "name_action_resource": "Ventilador",
                "comparator_action": "igual",
                "unit_action": "state",
                "meaning_action": "turn_on",
                "variable_action": "on",
                "type_variable_action": "string"
            }
        }
class ECAStateListDTO(BaseModel):
    """DTO para una lista de estados de ECAs"""
    ecas: List[List[str]] = Field(
        ..., 
        description="Lista de tuplas [nombre_eca, estado]",
        json_schema_extra={
            "example": [
                ["ECA1", "off"],
                ["ECA2", "on"],
                ["ECA3", "off"]
            ]
        }
    )