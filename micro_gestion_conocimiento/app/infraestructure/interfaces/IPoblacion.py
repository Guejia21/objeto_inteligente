
from pyparsing import ABC, abstractmethod

"""Interfaz de Población de la Ontología OOS."""
class IPoblacion(ABC):
    @abstractmethod
    def poblarMetadatosObjeto(self, diccionarioObjeto:dict, listaRecursos:dict) -> str:
        """Pobla los metadatos del objeto inteligente en la base de conocimiento."""