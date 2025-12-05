import os as uos

class Config:
    # Servidor
    HOST = '0.0.0.0'
    PORT = 8003

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
    WIFI_SSID = 'ejemplo'
    WIFI_PASS = 'ejemplo'
    # Configuración del broker MQTT    
    BROKER_HOST = "127.0.0.1"
    MQTT_PORT = 1884
    REGISTER_DATASTREAMS_QUEUE_NAME = 'register_datastreams_queue'    
    # Configuración ThingsBoard
    THINGSBOARD_HOST: str = "localhost"
    THINGSBOARD_PORT: int = 1883
    THINGSBOARD_ACCESS_TOKEN: str = "YOUR_THINGSBOARD_ACCESS_TOKEN"
    THINGSBOARD_TELEMETRY_TOPIC: str = "v1/devices/me/telemetry"
    TELEMETRY_PUBLISH_INTERVAL: int = 5  # Segundos
    THINGSBOARD_TOKEN = None