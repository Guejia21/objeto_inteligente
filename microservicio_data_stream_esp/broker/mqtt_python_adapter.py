"""Publicación y suscripción a un broker MQTT usando las librerias de python estándar"""
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
from broker.broker_interface import BrokerInterface
from config import Config
import asyncio

class MQTTPythonAdapter(BrokerInterface):
    def __init__(self, client_id, broker, user=None, password=None, port=1883):
        self.client = mqtt.Client(client_id=client_id, callback_api_version=CallbackAPIVersion.VERSION1)
        
        def on_connect(client, userdata, flags, rc):
            self.conectado = (rc == 0)
            if rc != 0:
                print(f"MQTT Conexión fallida (rc={rc})")
                
        def on_disconnect(client, userdata, rc):
            self.conectado = False
            if rc != 0:
                print("MQTT Desconectado inesperadamente")
            
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        
        if user:
            self.client.username_pw_set(user, password or "")
            
        self.broker = broker
        self.port = port
        self.conectado = False        

    def __conectar(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            import time
            timeout = 5
            while not self.conectado and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
                
            if self.conectado:
                print(f"MQTT Conectado a {self.broker}:{self.port}")
                
        except Exception as e:
            print(f"Error conectando MQTT: {e}")
            self.conectado = False

    async def publicar(self, topico, mensaje):
        if not self.conectado:
            self.__conectar()
            
        if self.conectado:
            try:
                result = self.client.publish(topico, mensaje, qos=1)
                result.wait_for_publish(timeout=5)
                return result.rc == mqtt.MQTT_ERR_SUCCESS
            except Exception as e:
                print(f"Error publicando: {e}")
                return False
        return False

    async def suscribirse(self, topico, callback):
        while not self.conectado:
            self.__conectar()
            if not self.conectado:
                await asyncio.sleep(1)
        
        def on_message(client, userdata, msg):
            callback(msg.topic, msg.payload.decode())

        self.client.on_message = on_message
        self.client.subscribe(topico)
        print(f"Suscrito a: {topico}")


# Broker para comunicación interna (Mosquitto)
mosquitto_broker = MQTTPythonAdapter(
    client_id="datastream_service_mosquitto",
    broker=Config.BROKER_HOST,
    port=Config.MQTT_PORT 
)

# Broker para ThingsBoard
tb_broker = MQTTPythonAdapter(
    client_id="datastream_service_tb",
    broker=Config.THINGSBOARD_HOST,
    user=Config.THINGSBOARD_ACCESS_TOKEN,
    password="",
    port=Config.THINGSBOARD_PORT
)