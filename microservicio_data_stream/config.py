import uos

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
    MQTT_PORT = 1883
    REGISTER_DATASTREAMS_QUEUE_NAME = 'register_datastreams_queue'
