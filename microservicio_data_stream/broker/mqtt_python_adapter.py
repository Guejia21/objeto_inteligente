"""Publicación y suscripción a un broker MQTT usando las librerias de python estándar"""
import asyncio
from paho.mqtt.client import CallbackAPIVersion
from broker.broker_interface import BrokerInterface


class MQTTPythonAdapter(BrokerInterface):
    def __init__(self, client_id, broker, user=None, password=None, port=1883):
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client(client_id=client_id,callback_api_version=CallbackAPIVersion.VERSION1)        
        if user and password:
            self.client.username_pw_set(user, password)
        self.broker = broker
        self.port = port
        self.conectado = False

    def __conectar(self):
        try:
            self.client.connect(self.broker, self.port)
            self.conectado = True
            print("Conectado al broker MQTT")
        except Exception as e:
            print(f"Error conectando a MQTT: {e}")
            self.conectado = False

    async def publicar(self, topico, mensaje):
        if not self.conectado:
            self.__conectar()
        if self.conectado:
            try:
                self.client.publish(topico, mensaje)                
            except Exception as e:
                print(f"Error publicando en MQTT: {e}")

    async def suscribirse(self, topico, callback):
        import threading
        # Intentar conectar sin bloquear indefinidamente
        while not self.conectado:
            print(f"Intentando conectar a MQTT broker...")
            await asyncio.sleep(0)  # Yield control
            self.__conectar()
            if not self.conectado:
                print("Reintentando en 5 segundos...")
                await asyncio.sleep(5)  # Espera asíncrona entre reintentos
        
        def on_message(client, userdata, msg):
            callback(msg.topic, msg.payload.decode())

        self.client.on_message = on_message
        self.client.subscribe(topico)
        print(f"Suscrito al tópico: {topico}")

        # Ejecutar el loop de MQTT en un hilo separado
        def mqtt_loop():
            self.client.loop_forever()

        thread = threading.Thread(target=mqtt_loop)
        thread.start()
        
        while True:
            await asyncio.sleep(1)  # Mantener la función asíncrona activa