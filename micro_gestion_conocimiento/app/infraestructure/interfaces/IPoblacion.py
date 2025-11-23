
from pyparsing import ABC, abstractmethod

"""Interfaz que define todos los métodos de población de la Ontología OOS."""
class IPoblacion(ABC):
    @abstractmethod
    def poblarMetadatosObjeto(self, diccionarioObjeto:dict, listaRecursos:dict) -> bool:
        """Pobla los metadatos del objeto inteligente en la base de conocimiento."""
    @abstractmethod
    def poblarECA(self, diccionarioECA:dict)->bool:
        """Pobla las reglas ECA en la base de conocimiento."""
    