from abc import ABC, abstractmethod

# Definición de la interfaz ILogPanel para publicar logs 
class ILogPanelMQTT(ABC):
    @abstractmethod    
    async def Publicar(self, topic: str, message):
        pass
    @abstractmethod
    async def suscribir(self, topic: str, callback):
        pass
    @abstractmethod
    async def PubLog(self, key: str, id_emisor: int, nombre_emisor: str, id_receptor: int, nombre_receptor: str, elemento: str, estado: str):
        pass
    @abstractmethod
    async def PubUserLog(self, entidad_interes: str, objeto: str, recurso: str, estado: str):
        pass
    @abstractmethod
    async def PubRawLog(self, objeto: str, recurso: str, value: str):
        pass