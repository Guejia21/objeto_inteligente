from pydantic import BaseModel
from typing import Optional

class Usuario(BaseModel):
    email: str
    osid: str
    autenticado: bool = False
    
    def verificar_autenticacion(self) -> bool:
        # Lógica similar a ModuloDePersonalizacion.verificarUsuario del legacy
        # Por ahora simulamos la verificación
        return self.autenticado
