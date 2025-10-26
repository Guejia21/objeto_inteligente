from abc import ABC, abstractmethod

class IRepository(ABC):

    @abstractmethod
    def save_object_metadata(self, metadata: dict):
        """Guarda los metadatos del objeto inteligente."""
        pass

    @abstractmethod
    def get_object_metadata(self) -> dict:
        """Obtiene los metadatos del objeto inteligente."""
        pass
    @abstractmethod
    def is_object_metadata_exists(self) -> bool:
        """Verifica si los metadatos del objeto inteligente existen."""
        pass
