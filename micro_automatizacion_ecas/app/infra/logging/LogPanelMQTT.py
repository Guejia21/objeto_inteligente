from infra.logging.ILogPanelMQTT import ILogPanelMQTT 
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
import asyncio
from config import settings
#Implementación concreta de la interfaz ILogPanel que publica logs a través de MQTT


class LogPanelMQTT(ILogPanelMQTT):
    _instance = None  # Variable de clase para almacenar la única instancia
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LogPanelMQTT, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = mqtt.Client(
                client_id="P1", 
                callback_api_version=CallbackAPIVersion.VERSION1
            )
            try:
                cls._instance.client.connect(settings.BROKER_HOST, settings.BROKER_PORT, 60)
                cls._instance.client.loop_start()
            except Exception as e:
                print(f"Error al conectar con el broker MQTT: {e}")
                cls._instance.client = None
        return cls._instance

    async def Publicar(self, topic: str, message):
        if not self.client:
            print("No se puede publicar, no hay conexión con el broker MQTT")
            return
        try:
            await asyncio.to_thread(self.client.publish, topic, message)
        except Exception as e:
            print(f"Error al publicar en el broker MQTT: {e}")

    async def PubLog(self, key: str, id_emisor: int, nombre_emisor: str, id_receptor: int, nombre_receptor: str, elemento: str, estado: str):
        data = {
            "key": key,
            "id_emisor": id_emisor,
            "nombre_emisor": nombre_emisor,
            "id_receptor": id_receptor,
            "elemento": elemento,
            "estado": estado,            
        }
        message = json.dumps(data)
        channel = "PanelLog"
        try:
            await self.Publicar(channel, message)
        except Exception as e:
            print(f"Error al publicar en LogPanel: {e}")

    async def PubUserLog(self, entidad_interes: str, objeto: str, recurso: str, estado: str):
        data = {
            "entidad_interes": entidad_interes,
            "objeto": objeto,
            "recurso": recurso,
            "estado": estado,            
        }
        message = json.dumps(data)
        channel = "UserLog"
        try:
            await self.Publicar(channel, message)
        except Exception as e:
            print(f"Error al publicar en UserLog: {e}")

    async def PubRawLog(self, objeto: str, recurso: str, value: str):
        data = {
            "objeto": objeto,
            "recurso": recurso,
            "value": value
        }
        message = json.dumps(data)
        channel = "RawLog"
        try:
            await self.Publicar(channel, message)
        except Exception as e:
            print(f"Error al publicar en RawLog: {e}")
