from time import time
from infraestructure.logging import ILogPanel
import paho.mqtt.client as mqtt
import json
import asyncio
#Implementación concreta de la interfaz ILogPanel que publica logs a través de MQTT

broker = "" # Dirección del broker MQTT (Potencialmente será mosquitto)

class LogPanel(ILogPanel):
    def __init__(self):
        self.client = mqtt.Client()
        try:
            self.client.connect(broker, 1883, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error al conectar con el broker MQTT: {e}")
            self.client = None

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
