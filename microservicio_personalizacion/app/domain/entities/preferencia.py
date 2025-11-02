from pydantic import BaseModel
from typing import Dict, Any, Optional

class Preferencia(BaseModel):
    email: str
    osid: str
    osidDestino: str
    contrato: Dict[str, Any]
    
    def validar_contrato(self) -> bool:
        """Valida la estructura del contrato ECA similar al sistema legacy"""
        campos_obligatorios = ['evento', 'accion']
        if not all(campo in self.contrato for campo in campos_obligatorios):
            return False
        
        # Validaciones específicas del contrato ECA
        evento = self.contrato.get('evento', {})
        accion = self.contrato.get('accion', {})
        
        return all([
            'recurso' in evento,
            'operador' in evento,
            'valor' in evento,
            'recurso' in accion,
            'valor' in accion
        ])
