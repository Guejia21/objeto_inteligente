from pydantic import BaseModel
from typing import Optional
from .evento_eca import EventoECA
from .accion_eca import AccionECA

class ECA(BaseModel):
    name_eca: str
    eca_state: str = "off"  # on/off como en el legacy
    eventoECA: EventoECA
    accionECA: AccionECA
    user_eca: Optional[str] = "system"  # default como en legacy
    interest_entity_eca: Optional[str] = None
    
    def activar(self):
        """Cambia estado a 'on' como en SetEcaState del legacy"""
        self.eca_state = "on"
    
    def desactivar(self):
        """Cambia estado a 'off' como en SetEcaState del legacy"""
        self.eca_state = "off"
    
    @classmethod
    def from_legacy_dict(cls, data: dict) -> 'ECA':
        """Crea ECA desde diccionario del sistema legacy (ConsultasOOS.getEca)"""
        evento = EventoECA.from_legacy_dict(data)
        accion = AccionECA.from_legacy_dict(data)
        
        return cls(
            name_eca=data.get("name_eca", ""),
            eca_state=data.get("eca_state", "off"),
            eventoECA=evento,
            accionECA=accion,
            user_eca=data.get("user_eca", "system"),
            interest_entity_eca=data.get("interest_entity_eca")
        )
    
    def to_legacy_dict(self) -> dict:
        """Convierte a formato diccionario compatible con el sistema legacy"""
        return {
            "name_eca": self.name_eca,
            "eca_state": self.eca_state,
            "user_eca": self.user_eca,
            "interest_entity_eca": self.interest_entity_eca,
            # Datos del evento
            "id_event_object": self.eventoECA.objEvento,
            "ip_event_object": self.eventoECA.ip_event_object,
            "id_event_resource": self.eventoECA.id_event_resource,
            "name_event_resource": self.eventoECA.name_event_resource,
            "name_event_object": self.eventoECA.name_event_object,
            "meaning_condition": self.eventoECA.signCondicion,
            "unit_condition": self.eventoECA.unidadCondicion,
            "variable_condition": self.eventoECA.variableCondicion,
            "comparator_condition": self.eventoECA.comparadorCondicion,
            # Datos de la acción
            "id_action_object": self.accionECA.objAccion,
            "ip_action_object": self.accionECA.ip_action_object,
            "id_action_resource": self.accionECA.id_action_resource,
            "name_action_resource": self.accionECA.name_action_resource,
            "name_action_object": self.accionECA.name_action_object,
            "meaning_action": self.accionECA.signAccion,
            "unit_action": self.accionECA.unidadAccion,
            "variable_action": self.accionECA.variableAccion,
            "comparator_action": self.accionECA.comparadorAccion
        }
