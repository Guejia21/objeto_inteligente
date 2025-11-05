from pydantic import BaseModel
from typing import Optional

class EventoECA(BaseModel):
    objEvento: str  # ID del objeto origen
    id_event_resource: str  # Recurso del evento
    name_event_resource: str
    name_event_object: str
    ip_event_object: Optional[str] = ""
    signCondicion: str  # Descripción de la condición
    unidadCondicion: str
    variableCondicion: str
    comparadorCondicion: str  # mayor, menor, igual, etc.
    
    @classmethod
    def from_legacy_dict(cls, data: dict) -> 'EventoECA':
        """Crea EventoECA desde diccionario del sistema legacy"""
        return cls(
            objEvento=data.get("id_event_object", ""),
            id_event_resource=data.get("id_event_resource", ""),
            name_event_resource=data.get("name_event_resource", ""),
            name_event_object=data.get("name_event_object", ""),
            ip_event_object=data.get("ip_event_object", ""),
            signCondicion=data.get("meaning_condition", ""),
            unidadCondicion=data.get("unit_condition", ""),
            variableCondicion=data.get("variable_condition", ""),
            comparadorCondicion=data.get("comparator_condition", "")
        )
