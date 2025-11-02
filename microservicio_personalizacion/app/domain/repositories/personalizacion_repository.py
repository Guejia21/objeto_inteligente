from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.eca import ECA

class PersonalizacionRepository(ABC):
    """Interface para el repositorio de personalización (Patrón Repository)"""
    
    @abstractmethod
    async def guardar_eca(self, eca: ECA) -> bool:
        pass
    
    @abstractmethod
    async def obtener_eca(self, nombre_eca: str) -> Optional[ECA]:
        pass
    
    @abstractmethod
    async def listar_ecas_usuario(self, email: str) -> List[ECA]:
        pass
    
    @abstractmethod
    async def listar_todos_ecas(self) -> List[ECA]:
        pass
    
    @abstractmethod
    async def cambiar_estado_eca(self, nombre_eca: str, estado: str) -> bool:
        pass
    
    @abstractmethod
    async def desactivar_ecas_usuario(self, email: str) -> List[str]:
        pass
    
    @abstractmethod
    async def eliminar_eca(self, nombre_eca: str) -> bool:
        pass
    
    @abstractmethod
    async def verificar_usuario(self, email: str) -> bool:
        pass