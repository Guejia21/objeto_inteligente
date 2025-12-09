"""
Microservicio Data Stream para ESP32
Con telemetría a ThingsBoard
"""

try:
    import ujson as json
except ImportError:
    import json

from lib.microdot.microdot import Microdot
from routes.datastreams import register_routes
from config import Config
import gc
import time

# Liberar memoria
gc.collect()

print("=" * 50)
print("Datastream Service - ESP32")
print("=" * 50)

# Crear aplicación
app = Microdot()

# Registrar rutas
register_routes(app)

# ===== INFO =====
print("=" * 50)
print("   OSID: " + str(Config.OSID))
print("   Title: " + str(Config.TITLE))
print("   Host: " + str(Config.HOST) + ":" + str(Config.PORT))
print("=" * 50)

# ===== CONECTAR WIFI =====
print("\nConectando WiFi...")
from utils.wifi_manager import wifi_manager

if wifi_manager.connect(timeout=15):
    print("\nWiFi OK - IP: " + wifi_manager.get_ip())
else:
    print("\nWiFi FALLO - Funcionalidad limitada")

# ===== INICIALIZAR TELEMETRÍA =====
telemetry_service = None

if Config.TELEMETRY_ENABLED and wifi_manager.connected:
    print("\nInicializando servicio de telemetria...")
    
    from broker.mqtt_micropython import MQTTMicroPythonAdapter
    from services.telemetry_service import TelemetryService
    from routes.datastreams import datastream_service
    
    # ✅ Crear cliente MQTT para ThingsBoard (solo con username/token)
    print("Creando cliente MQTT ThingsBoard...")
    tb_mqtt = MQTTMicroPythonAdapter(
        broker=Config.THINGSBOARD_HOST,
        port=Config.THINGSBOARD_PORT,
        client_id="tb_" + Config.OSID,
        username=Config.THINGSBOARD_ACCESS_TOKEN,  # Token como username
        password=None  # ThingsBoard no usa password
    )
    
    # Crear servicio de telemetría
    telemetry_service = TelemetryService(datastream_service, tb_mqtt)
    
    # Conectar a ThingsBoard
    if telemetry_service.connect():
        print("Servicio de telemetria listo\n")
    else:
        print("No se pudo conectar telemetria (continuando sin ella)\n")
        telemetry_service = None
else:
    print("\nTelemetria deshabilitada\n")

print("Servidor HTTP iniciando...")
print("Memoria disponible: " + str(gc.mem_free()) + " bytes")
print("\nPresiona Ctrl+C para detener\n")

# ===== KEEP-ALIVE Y TELEMETRÍA =====
last_wifi_check = time.time()
last_telemetry = time.time()

@app.after_request
def after_request_handler(request, response):
    """Hook después de cada request"""
    global last_wifi_check, last_telemetry
    
    now = time.time()
    
    # 1. Verificar WiFi cada 30s
    if now - last_wifi_check > 30:
        if not wifi_manager.keep_alive():
            print("WiFi reconectado!")
        last_wifi_check = now
    
    # 2. Publicar telemetría según intervalo
    if telemetry_service and (now - last_telemetry > Config.TELEMETRY_INTERVAL):
        try:
            telemetry_service.loop()
            last_telemetry = now
        except Exception as e:
            print("Error en telemetry loop: " + str(e))
    return response

# ===== INICIO =====
try:
    print("Starting server on " + Config.HOST + ":" + str(Config.PORT))
    print("IP del servidor: " + str(wifi_manager.get_ip()))
    
    if telemetry_service:
        print("\nTelemetria:")
        print("  Publicando cada " + str(Config.TELEMETRY_INTERVAL) + "s")
        print("  Topic: " + Config.THINGSBOARD_TELEMETRY_TOPIC)
    
    print("\nEsperando peticiones...\n")
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
    
except KeyboardInterrupt:
    print("\nServidor interrumpido")
    if telemetry_service:
        telemetry_service.disconnect()
    wifi_manager.disconnect()
    
except Exception as e:
    print("\nError: " + str(e))
    import sys
    if hasattr(sys, 'print_exception'):
        sys.print_exception(e)
    if telemetry_service:
        telemetry_service.disconnect()
    wifi_manager.disconnect()
    
finally:
    print("Adios!")
    gc.collect()