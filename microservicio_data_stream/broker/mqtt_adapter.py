"""Adapter para el broker MQTT"""
import asyncio
from broker.broker_interface import BrokerInterface
from lib.umqtt.simple import MQTTClient

class MQTTAdapter(BrokerInterface):
    def __init__(self, client_id, broker, user=None, password=None, port=1883):
        self.client = MQTTClient(client_id, broker, user=user, password=password, port=port)
        self.conectado = False

    def __conectar(self):
        try:
            self.client.connect()
            self.conectado = True
            print("Conectado al broker MQTT")
        except Exception as e:
            print(f"Error conectando a MQTT: {e}")
            self.conectado = False

    def publicar(self, topico, mensaje):
        if not self.conectado:
            self.__conectar()
        if self.conectado:
            self.client.publish(topico.encode(), mensaje.encode())

    async def suscribirse(self, topico, callback):
        # Intentar conectar sin bloquear indefinidamente
        while not self.conectado:
            print(f"Intentando conectar a MQTT broker...")
            await asyncio.sleep(0)  # Yield control
            self.__conectar()
            if not self.conectado:
                print("Reintentando en 5 segundos...")
                await asyncio.sleep(5)  # Espera asíncrona entre reintentos
        
        self.client.set_callback(callback)
        self.client.subscribe(topico.encode())
        print(f"Suscrito al tópico: {topico}")
        
        while True:
            if self.conectado:
                try:
                    self.client.check_msg()  # No bloqueante
                except Exception as e:
                    print(f"Error en MQTT: {e}")
                    self.conectado = False
            await asyncio.sleep(0.1)