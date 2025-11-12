
import os
from pyparsing import ABC, abstractmethod
from app import config
from app.infraestructure.logging.Logging import logger
"""Interfaz de Población de la Ontología OOS."""
class IPoblacion(ABC):        

    @abstractmethod
    def registroInteraccionUsuarioObjeto(self, email, idDataStream, comando, osid, dateInteraction):
        """Registra la interacción del usuario con el objeto."""
        pass