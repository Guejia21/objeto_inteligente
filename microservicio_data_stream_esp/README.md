# README - Microservicio Data Stream para ESP32

## Descripción General

Este proyecto implementa un microservicio de gestión de datastreams en un ESP32 utilizando MicroPython. El sistema expone una API HTTP REST para controlar actuadores (LEDs, relés) y leer sensores (RTC, temperatura, etc.), además de publicar telemetría automática a ThingsBoard vía MQTT.

## Características Principales

- **API HTTP REST**: Servidor web en el ESP32 accesible por WiFi
- **Gestión de Datastreams**: Control de actuadores y lectura de sensores
- **Telemetría MQTT**: Publicación automática de datos a ThingsBoard
- **WiFi Persistente**: Conexión WiFi estable con reconexión automática
- **Optimización de Memoria**: Diseñado para funcionar en ESP32 con recursos limitados
- **Arquitectura Modular**: Código organizado en servicios, rutas y adaptadores

## Arquitectura del Sistema
```text
microservicio_data_stream_esp/
├── boot.py                      # Configuración inicial del ESP32
├── main.py                      # Punto de entrada principal
├── config.py                    # Configuración global (WiFi, MQTT, ThingsBoard)
│
├── broker/                      # Adaptadores MQTT
│   └── mqtt_micropython.py      # Cliente MQTT para MicroPython
│
├── hardware/                    # Abstracción de hardware
│   └── esp32_hw_adapter.py      # Ejecutor de scripts de hardware
│
├── lib/                         # Librerías externas
│   ├── microdot/                # Framework web ligero
│   └── umqtt/                   # Cliente MQTT simple
│
├── routes/                      # Endpoints HTTP
│   └── datastreams.py           # Rutas de la API REST
│
├── services/                    # Lógica de negocio
│   ├── datastream_service.py    # Gestión de datastreams
│   └── telemetry_service.py     # Publicación de telemetría
│
├── storage/                     # Almacenamiento
│   ├── executables/             # Scripts de hardware (on_led.py, get_rtc.py, etc.)
│   └── metadata/                # Metadata del dispositivo
│       └── metadata.py
│
└── utils/                       # Utilidades
    ├── wifi_manager.py          # Gestión de conexión WiFi
    └── response.py              # Formateador de respuestas JSON
```
# Instalación y Configuración

## 1. Preparar el Entorno de Desarrollo
Configura tu entorno para trabajar con ESP32 y MicroPython.
```sh
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar herramientas
pip install esptool adafruit-ampy
```

## 2. Flashear MicroPython en el ESP32
Utiliza herramientas como **esptool.py** o **Thonny** para cargar MicroPython.
```sh
# Descargar firmware de MicroPython
wget https://micropython.org/resources/firmware/ESP32_GENERIC-20250911-v1.26.1.bin

# Borrar flash del ESP32
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

# Flashear MicroPython
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20250911-v1.26.1.bin
```

## 3. Configurar el Proyecto

### Editar `config.py` con tus credenciales:
```python
# WiFi
WIFI_SSID = 'TU_RED_WIFI'
WIFI_PASS = 'TU_PASSWORD'

# ThingsBoard
THINGSBOARD_HOST = "IP_DE_THINGSBOARD"
THINGSBOARD_PORT = 1883
THINGSBOARD_ACCESS_TOKEN = "TU_TOKEN_DE_DISPOSITIVO"

# Telemetría
TELEMETRY_ENABLED = True
TELEMETRY_INTERVAL = 10  # Segundos entre publicaciones
```

### Editar `storage/metadata/metadata.py`:
```python
DEVICE_INFO = {
    "osid": "TU_ID_DISPOSITIVO",
    "title": "ESP32 Smart Object",
    "ip": "0.0.0.0"
}

DATASTREAMS = [
    {
        "datastream_id": "led_status",
        "datastream_format": "boolean",
        "datastream_type": "actuator"
    },
    # Agregar más datastreams según necesites
]
```
## 4. Desplegar en el ESP32
```sh
# Dar permisos de ejecución al script de deploy
chmod +x deploy_esp.sh

# Ejecutar despliegue completo
./deploy_esp.sh

# El script:
# 1. Configura permisos del puerto serial
# 2. Activa el entorno virtual
# 3. Sube todos los archivos al ESP32
# 4. Resetea el dispositivo
```
## 5. Verificar el Despliegue
Conéctate por serial (ej. `picocom`, `minicom`, `screen`).
```sh
# Conectar al monitor serial
picocom /dev/ttyUSB0 -b 115200

# Deberías ver:
# ========================================
#   ESP32 DataStream Service
# ========================================
# ...
# WiFi conectado: 192.168.X.XXX
# ThingsBoard MQTT conectado!
# Starting server on 0.0.0.0:8003
```
**Salir de picocom:** `Ctrl+A` luego `Ctrl+X`
## Uso de la API
### Endpoints disponibles
```text
GET /Datastreams/health
GET /Datastreams/SendState?osid={osid}
GET /Datastreams/SendData?osid={osid}&variableEstado={id}&tipove=1
POST /Datastreams/SetDatastream?osid={osid}&idDataStream={id}&comando={on|off}
```
### Ejemplos con curl
```sh
# Variables
IP_ESP32="192.168.8.177"
OSID="ObjetoESP32"

# Obtener estado
curl "http://$IP_ESP32:8003/Datastreams/SendState?osid=$OSID"

# Encender LED
curl -X POST "http://$IP_ESP32:8003/Datastreams/SetDatastream?osid=$OSID&idDataStream=led_status&comando=on"

# Ver telemetría
curl "http://$IP_ESP32:8003/telemetry/status"
```

# Telemetría
## Formato de datos publicados
El servicio publica automáticamente en formato JSON (Ejemplo de dos datastreams llamados `led` y `relay` ):
```json
{
  "led": false,    
  "relay": true,
  "_mem_free": 78000
}
```
# Nota
Si después de ejecutar `deploy.sh` e ingresar a la consola usando `picocom` no se ejecuta el programa ni sale algo parecido a:
```text
========================================
  ESP32 DataStream Service
========================================
Debug ESP desactivado
CPU frecuencia: 160.0MHz
WiFi inicializado (inactivo)
Memoria libre: 155504 bytes

Boot completado - Iniciando main.py...
========================================

Hardware adapter inicializado (ESP32)
DatastreamService inicializado (2 datastreams)

Conectando WiFi...
=== WiFi CONECTADO ===
  IP:      192.168.8.177
  Gateway: 192.168.8.1
======================

Conectando a ThingsBoard MQTT...
MQTT conectado OK: 192.168.8.209:========================================
  ESP32 DataStream Service
========================================
Debug ESP desactivado
CPU frecuencia: 160.0MHz
WiFi inicializado (inactivo)
Memoria libre: 155504 bytes

Boot completado - Iniciando main.py...
========================================

Hardware adapter inicializado (ESP32)
DatastreamService inicializado (2 datastreams)

Conectando WiFi...
=== WiFi CONECTADO ===
  IP:      192.168.8.177
  Gateway: 192.168.8.1
======================

Conectando a ThingsBoard MQTT...
MQTT conectado OK: 192.168.8.209:1883

Starting server on 0.0.0.0:8003
Esperando peticiones...
```
Presiona `Enter` hasta que aparezca en la consola `>>>` posteriormente presiona `Ctrl+D`. De esa manera se reinicia la esp y debería de cargar el `boot.py` 