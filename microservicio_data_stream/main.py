import json as json
from lib.microdot.microdot import Microdot
from broker.broker_interface import consumer_mqtt, publicar_valores, publicacion_task
#from broker.mqtt_adapter import MQTTAdapter
from broker.mqtt_python_adapter import mosquitto_broker,tb_broker
from routes.datastreams import register_routes
from config import Config
#import network #Activar si se usa ESP32 con WiFi
import asyncio

# Crear aplicación
app = Microdot()
# Configurar broker MQTT cuando se desea usar microPython
"""broker = MQTTAdapter(
    client_id="datastream_service",
    #broker=Config.OBJECT_IP,
    broker=Config.BROKER_HOST, #Usar localhost para pruebas locales
    port=Config.MQTT_PORT
)"""

# Registrar rutas
register_routes(app)

#Configuración de WiFi (si aplica)
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(Config.WIFI_SSID, Config.WIFI_PASS)
    while not wlan.isconnected():
        pass
    print("WiFi conectada:", wlan.ifconfig())


# Ejecutar servidor
async def main():
    print(f"   Datastream Service iniciando en {Config.HOST}:{Config.PORT}")
    print(f"   OSID: {Config.OSID}")
    print(f"   Title: {Config.TITLE}")
    #conectar_wifi()
    # Iniciar servidor
    asyncio.create_task(app.start_server(host=Config.HOST, port=Config.PORT))    
    if Config.OSID:
        # Iniciar publicación periódica si ya hay OSID
        global publicacion_task
        publicacion_task = asyncio.create_task(
            publicar_valores(tb_broker, Config.OSID, interval=Config.TELEMETRY_PUBLISH_INTERVAL)
        )
    else:
        #Si el objeto no está incializado, esperar a que se inicialice
        print("Esperando inicialización del objeto...")
        asyncio.create_task(consumer_mqtt(mosquitto_broker))
    while True:
        await asyncio.sleep(1)
asyncio.run(main())