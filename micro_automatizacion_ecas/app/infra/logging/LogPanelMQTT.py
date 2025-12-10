from infra.logging.ILogPanelMQTT import ILogPanelMQTT 
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
import asyncio
from config import settings


class LogPanelMQTT(ILogPanelMQTT):
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LogPanelMQTT, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = mqtt.Client(
                client_id="micro_ecas", 
                callback_api_version=CallbackAPIVersion.VERSION1
            )
            cls._instance._loop = None
            cls._instance._callbacks = {}  # Guardar callbacks por topic
            try:
                cls._instance.client.connect(settings.BROKER_HOST, settings.BROKER_PORT, 60)
                cls._instance.client.loop_start()
                print(f" MQTT conectado a {settings.BROKER_HOST}:{settings.BROKER_PORT}")
            except Exception as e:
                print(f" Error conectando MQTT: {e}")
                cls._instance.client = None
        return cls._instance

    def set_event_loop(self, loop):
        """Configura el event loop para usar en callbacks"""
        self._loop = loop

    async def Publicar(self, topic: str, message):
        if not self.client:
            print("No hay conexión MQTT")
            return
        try:
            result = self.client.publish(topic, message, qos=1)
            result.wait_for_publish(timeout=5)
        except Exception as e:
            print(f"Error publicando: {e}")
    
    async def suscribir(self, topic: str, callback):
        if not self.client:
            print("No hay conexión MQTT para suscribir")
            return
            
        try:
            # Obtener el loop actual y guardarlo
            loop = asyncio.get_running_loop()
            self._loop = loop
            
            # Guardar el callback async
            self._callbacks[topic] = callback
            
            def on_message(client, userdata, msg):
                """Callback síncrono del broker - se ejecuta en hilo de paho"""
                topic = msg.topic
                payload = msg.payload.decode()
                
                # Buscar el callback registrado para este topic
                cb = self._callbacks.get(topic)
                if cb is None:
                    print(f"No hay callback para topic: {topic}")
                    return
                
                if self._loop is None or not self._loop.is_running():
                    print("Event loop no disponible")
                    return
                
                # Ejecutar el callback async en el event loop principal
                try:
                    future = asyncio.run_coroutine_threadsafe(cb(topic, payload), self._loop)
                    # No esperamos el resultado para no bloquear el hilo de paho
                except Exception as e:
                    print(f"Error ejecutando callback: {e}")
            
            # Configurar el callback general de mensajes
            self.client.on_message = on_message
            
            # Suscribirse al topic
            result, mid = self.client.subscribe(topic, qos=1)
            if result == mqtt.MQTT_ERR_SUCCESS:
                print(f"Suscrito a: {topic}")
            else:
                print(f"Error suscribiendo a {topic}: {result}")
                
        except Exception as e:
            print(f"Error en suscripción: {e}")
            import traceback
            traceback.print_exc()
    
    async def PubLog(self, key: str, id_emisor: int, nombre_emisor: str, id_receptor: int, nombre_receptor: str, elemento: str, estado: str):
        data = {
            "key": key,
            "id_emisor": id_emisor,
            "nombre_emisor": nombre_emisor,
            "id_receptor": id_receptor,
            "elemento": elemento,
            "estado": estado,            
        }
        await self.Publicar("PanelLog", json.dumps(data))

    async def PubUserLog(self, entidad_interes: str, objeto: str, recurso: str, estado: str):
        data = {
            "entidad_interes": entidad_interes,
            "objeto": objeto,
            "recurso": recurso,
            "estado": estado,            
        }
        await self.Publicar("UserLog", json.dumps(data))

    async def PubRawLog(self, objeto: str, recurso: str, value: str):
        data = {
            "objeto": objeto,
            "recurso": recurso,
            "value": value
        }
        await self.Publicar("RawLog", json.dumps(data))