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
# Configurar broker MQTT
broker = MQTTAdapter(
    client_id="datastream_service",
    #broker=Config.OBJECT_IP,
    broker=Config.BROKER_HOST, #Usar localhost para pruebas locales
    port=Config.MQTT_PORT
) 
# Variable global para controlar la tarea de publicación
publicacion_task = None
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

async def publicar_valores(broker: BrokerInterface, osid: str, interval: int = 5):
    """
    Publica periódicamente los valores de los datastreams a través de MQTT
    
    Args:
        broker: Instancia del broker MQTT
        osid: ID del objeto inteligente
        interval: Intervalo en segundos entre publicaciones (default: 5s)
    """
    print(f"Iniciando publicación periódica de valores cada {interval}s...")
    
    while True:
        try:
            # Obtener estado actual de todos los datastreams
            estado = datastream_service.send_state(osid)
            estado_json = json.loads(estado)            
            
            # Validar que el estado sea válido y tenga datastreams
            if estado_json and isinstance(estado_json, dict):
                datastreams = estado_json.get("datastreams", [])                
                if datastreams:
                    # Formatear telemetría
                    telemetry = {}
                    for ds in datastreams:
                        ds_id = ds.get("datastream_id") or ds.get("variableEstado")
                        ds_value = ds.get("value") or ds.get("valor")
                        if ds_id and ds_value is not None:
                            telemetry[ds_id] = ds_value
                    
                    if telemetry:
                        # Publicar a ThingsBoard
                        topic = f"telemetry/{osid}"                         
                        await broker.publicar(topic, json.dumps(telemetry))                        
                    else:
                        print("No hay valores para publicar")
                else:
                    print("No hay datastreams disponibles aún")
            else:
                print(f"Estado inválido: {estado_json}")
                    
        except Exception as e:
            print(f"Error publicando valores: {e}")
        
        await asyncio.sleep(interval)
# Función para consumir mensajes del broker (Se usa la interfaz BrokerInterface para mayor abstracción)
async def consumer_mqtt(broker: BrokerInterface):
    global publicacion_task
    
    def recibir_datastreams(topic, msg):
        global publicacion_task
        
        print("Registrando datastream desde mensaje MQTT...")
        datastreams = util.convert_metadata_format(json.loads(msg))
        util.save_metadata(datastreams)
        util.create_executables(datastreams["datastreams"], datastreams["object"]["id"])
        datastream_service._load_metadata()
        print("Datastreams registrados correctamente.")
        
        # Cancelar tarea anterior si existe
        if publicacion_task and not publicacion_task.done():
            publicacion_task.cancel()
            print("Tarea de publicación anterior cancelada.")
        
        # Crear nueva tarea de publicación
        osid = datastreams["object"]["id"]
        publicacion_task = asyncio.create_task(
            publicar_valores(broker, osid, interval=Config.TELEMETRY_PUBLISH_INTERVAL)
        )
        print("Nueva tarea de publicación iniciada.")

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
    if Config.OSID:
        # Iniciar publicación periódica si ya hay OSID
        global publicacion_task
        publicacion_task = asyncio.create_task(
            publicar_valores(broker, Config.OSID, interval=Config.TELEMETRY_PUBLISH_INTERVAL)
        )
    while True:
        await asyncio.sleep(1)
asyncio.run(main())