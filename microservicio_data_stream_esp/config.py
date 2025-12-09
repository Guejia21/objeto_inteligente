import uos as uos
from storage.metadata.metadata import obtener_info_dispositivo


class Config:
    # Servidor
    HOST = '0.0.0.0'
    PORT = 8003
    DEBUG = True

    BASE_DIR = uos.getcwd()
    # Rutas (compatibles con MicroPython)
    PATH_EJECUTABLES = BASE_DIR + '/storage/executables/'
    PATH_METADATA = BASE_DIR + '/storage/metadata/'

    # Objeto (se carga dinámicamente desde metadata)
    OSID = None
    TITLE = None
    OBJECT_IP = None

    # Códigos de respuesta
    CODES = {
        'exitoso': '1000',
        'datastreamEncendido': '1001',
        'idIncorrecto': '1025',
        'dataStremNoExiste': '1026',
        'errorDatastream': '1027',
        'noImplementado': '1099'
    }
    # Configuración de WiFi
    WIFI_SSID = 'NexTech' # Cambiar
    WIFI_PASS = 'nextechOI'
    # Configuración del broker MQTT    
    BROKER_HOST = "192.168.8.209" 
    MQTT_PORT = 1883
    MOSQUITTO_TELEMETRY_TOPIC: str = "datastream/telemetry"
    REGISTER_DATASTREAMS_QUEUE_NAME = 'register_datastreams_queue'    
    # Configuración ThingsBoard
    THINGSBOARD_HOST: str = "192.168.8.209"
    THINGSBOARD_PORT: int = 1884
    THINGSBOARD_ACCESS_TOKEN: str = "h5jZTUMjxqEl0TzNIEO6"
    THINGSBOARD_TELEMETRY_TOPIC: str = "v1/devices/me/telemetry"
    # Configuración de telemetría
    TELEMETRY_ENABLED = True
    TELEMETRY_INTERVAL = 2  # Segundos entre publicaciones    

# Cargar metadatos del dispositivo
metadatos = obtener_info_dispositivo()
Config.OSID = metadatos.get('osid', 'ESP32_DEFAULT')
Config.TITLE = metadatos.get('title', 'ESP32 Device')
Config.OBJECT_IP = metadatos.get('ip', '0.0.0.0')