import ujson as json
from lib.microdot.microdot import Microdot
from broker.broker_interface import BrokerInterface
from broker.mqtt_adapter import MQTTAdapter
from routes.datastreams import register_routes
from routes.datastreams import datastream_service
from config import Config
from utils import util
#import network #Activar si se usa ESP32 con WiFi
import asyncio
# Crear aplicación
app = Microdot()
broker = MQTTAdapter(
    client_id="datastream_service",
    #broker=Config.OBJECT_IP,
    broker="127.0.0.1", #Usar localhost para pruebas locales
    port=Config.MQTT_PORT
) 
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
# Función para consumir mensajes del broker (Se usa la interfaz BrokerInterface para mayor abstracción)
async def consumer_mqtt(broker: BrokerInterface):
    def recibir_datastreams(topic, msg):
        print("Registrando datastream desde mensaje MQTT...")
        datastreams = util.convert_metadata_format(json.loads(msg))
        util.save_metadata(datastreams)
        util.generarEjecutables(datastreams["datastreams"], datastreams["object"]["id"])
        datastream_service._load_metadata()
        print("Datastreams registrados correctamente.")
        # Aquí se puede procesar el mensaje recibido

    await broker.suscribirse(Config.REGISTER_DATASTREAMS_QUEUE_NAME, recibir_datastreams)

# Ejecutar servidor
async def main():
    print(f"   Datastream Service iniciando en {Config.HOST}:{Config.PORT}")
    print(f"   OSID: {Config.OSID}")
    print(f"   Title: {Config.TITLE}")
    #conectar_wifi()
    # Iniciar servidor
    asyncio.create_task(app.start_server(host=Config.HOST, port=Config.PORT))
    # Iniciar suscripción a broker MQTT
    asyncio.create_task(consumer_mqtt(broker))
    while True:
        await asyncio.sleep(1)
asyncio.run(main())