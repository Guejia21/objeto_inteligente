from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IConsultasPerfilUsuario(ABC):
    #TODO Especificar los métodos abstractos para las consultas del perfil de usuario
    @abstractmethod
    def consultarPreferenciasUsuario(self) -> Dict[str, Any]:
        """Retorna las preferencias del usuario como un diccionario."""