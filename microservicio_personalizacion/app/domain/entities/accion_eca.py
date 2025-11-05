from pydantic import BaseModel
from typing import Optional

class AccionECA(BaseModel):
    objAccion: str  # ID del objeto destino
    id_action_resource: str  # Recurso de la acción
    name_action_resource: str
    name_action_object: str
    ip_action_object: Optional[str] = ""
    signAccion: str  # Descripción de la acción
    unidadAccion: str
    variableAccion: str
    comparadorAccion: str  # igual, sumar, restar, etc.
    
    @classmethod
    def from_legacy_dict(cls, data: dict) -> 'AccionECA':
        """Crea AccionECA desde diccionario del sistema legacy"""
        return cls(
            objAccion=data.get("id_action_object", ""),
            id_action_resource=data.get("id_action_resource", ""),
            name_action_resource=data.get("name_action_resource", ""),
            name_action_object=data.get("name_action_object", ""),
            ip_action_object=data.get("ip_action_object", ""),
            signAccion=data.get("meaning_action", ""),
            unidadAccion=data.get("unit_action", ""),
            variableAccion=data.get("variable_action", ""),
            comparadorAccion=data.get("comparator_action", "")
        )
