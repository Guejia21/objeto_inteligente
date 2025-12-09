from abc import ABC, abstractmethod
from typing import Dict, Any


class IPoblarPerfilUsuario(ABC):
    """Interfaz para poblar la ontología del perfil de usuario."""

    @abstractmethod
    def registroInteraccionUsuarioObjeto(
        self, 
        email: str, 
        idDataStream: str, 
        comando: str, 
        osid: str, 
        dateInteraction: str
    ) -> bool:
        """
        Registra una interacción del usuario con un objeto.
        
        Args:
            email: Correo electrónico del usuario
            idDataStream: Identificador del data stream
            comando: Comando ejecutado
            osid: Identificador del objeto inteligente
            dateInteraction: Fecha de la interacción (formato: "dd/mm/yy hh:mm:ss" o "00/00/00 00:00:00" para fecha actual)
        
        Returns:
            bool: True si el registro fue exitoso, False en caso contrario
        """
        pass

    @abstractmethod
    def editarSmartUsuario(self, diccObjetivo: Dict[str, Any]) -> None:
        """
        Edita un objetivo SMART del usuario.
        
        Args:
            diccObjetivo: Diccionario con la estructura:
                {
                    'name_objective': str,
                    'specific': str,
                    'start_date': str,  # formato: 'dd/mm/yyyy'
                    'Measurable': str,
                    'suitable_for': str,
                    'actcs': List[Dict[str, str]],  # [{'Número': str, 'Nombre': str, 'Fecha Inicio': str, 'Fecha Fin': str, 'Estado': str, 'Descripcion': str}]
                    'resource': List[Dict[str, str]]  # [{'Numero': str, 'Nombre': str}]
                }
        """
        pass

    @abstractmethod
    def registroSmartUsuario(self, diccObjetivo: Dict[str, Any]) -> None:
        """
        Registra un nuevo objetivo SMART del usuario.
        
        Args:
            diccObjetivo: Diccionario con la estructura:
                {
                    'name_objective': str,
                    'specific': str,
                    'start_date': str,  # formato: 'dd/mm/yyyy'
                    'Measurable': str,
                    'suitable_for': str,
                    'actcs': List[Dict[str, str]],  # [{'Número': str, 'Nombre': str, 'Fecha Inicio': str, 'Fecha Fin': str, 'Estado': str, 'Descripcion': str}]
                    'resource': List[Dict[str, str]]  # [{'Numero': str, 'Nombre': str}]
                }
        """
        pass