
import os
from pyparsing import ABC, abstractmethod
import config
from infraestructure.logging.Logging import logger
"""Interfaz de Población de la Ontología OOS."""
#TODO!!!!
class IPoblacion(ABC):        

    @abstractmethod
    def registroInteraccionUsuarioObjeto(self, email, idDataStream, comando, osid, dateInteraction):
        """Registra la interacción del usuario con el objeto."""
        pass