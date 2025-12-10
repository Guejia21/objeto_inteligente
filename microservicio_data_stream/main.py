"""
 * @file main.py
 * @brief Punto de entrada principal del Microservicio de Datastreams (Microdot)
 * @details
 * Servicio responsable de gestionar datastreams de objetos inteligentes usando Microdot framework (MicroPython).
 * 
 * Funcionalidades principales:
 * - Servidor HTTP asincrónico basado en Microdot
 * - Gestión de datastreams (sensores y actuadores)
 * - Publicación periódica de telemetría a ThingBoard y Mosquitto
 * - Consumo de mensajes MQTT para inicialización y actuaciones
 * - Cierre seguro con manejo de señales UNIX
 * - Soporte para WiFi en dispositivos ESP32
 * 
 * @see routes/datastreams.py para definición de endpoints
 * @see services/datastream_service.py para lógica de negocio
 * @see config.py para configuración del servicio
 * 
 * @author Sistema de Objetos Inteligentes
 * @version 1.0.0
 * @date 2024
"""

import json as json
import signal
from lib.microdot.microdot import Microdot
from broker.broker_interface import consumer_mqtt, publicar_valores, tb_publicacion_task, mosq_publicacion_task
#from broker.mqtt_adapter import MQTTAdapter
from broker.mqtt_python_adapter import mosquitto_broker, tb_broker
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

# Flag para controlar el cierre
shutdown_event = asyncio.Event()
running_tasks = []

#Configuración de WiFi (si aplica)
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(Config.WIFI_SSID, Config.WIFI_PASS)
    while not wlan.isconnected():
        pass
    print("WiFi conectada:", wlan.ifconfig())


async def shutdown():
    """
     * @brief Maneja el cierre seguro del servidor Microdot
     * @details
     * Coordina la detención ordenada de:
     * 1. Event loop - propaga shutdown_event
     * 2. Tareas asyncio - cancela todas las tareas en running_tasks
     * 3. Conexiones MQTT - cierra clientes mosquitto y ThingBoard
     * 4. Servidor HTTP - detiene Microdot
     * 
     * @return void
     * @see running_tasks lista de tareas en ejecución
     * @see mosquitto_broker cliente MQTT Mosquitto
     * @see tb_broker cliente MQTT ThingBoard
    """
    """Maneja el cierre seguro del servidor"""
    print("\nCerrando servidor...")
    shutdown_event.set()
    
    # Cancelar todas las tareas
    for task in running_tasks:
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    # Cerrar conexiones MQTT
    try:
        if hasattr(mosquitto_broker, 'client') and mosquitto_broker.client:
            mosquitto_broker.client.loop_stop()
            mosquitto_broker.client.disconnect()
    except Exception:
        pass
    
    try:
        if hasattr(tb_broker, 'client') and tb_broker.client:
            tb_broker.client.loop_stop()
            tb_broker.client.disconnect()
    except Exception:
        pass
    
    # Detener servidor Microdot
    try:
        app.shutdown()
    except Exception:
        pass
    
    print("Servidor cerrado correctamente")


# Ejecutar servidor
async def main():
    """
     * @brief Función principal que inicializa y ejecuta el servidor Microdot
     * @details
     * Secuencia de inicialización:
     * 1. Imprime configuración del servicio (HOST, PORT, OSID, TITLE)
     * 2. Registra manejadores de señales UNIX (SIGINT, SIGTERM) para shutdown seguro
     * 3. Inicia servidor Microdot asincrónico
     * 4. Si OSID está configurado:
     *    - Publica telemetría periódicamente a ThingBoard (si token disponible)
     *    - Publica telemetría periódicamente a Mosquitto
     * 5. Si OSID no está configurado: espera mensajes MQTT de inicialización
     * 6. Aguarda evento de shutdown
     * 
     * @return void (async)
     * @see shutdown() función invocada en cierre
     * @see Config configuración centralizada
     * @see publicar_valores tarea de publicación periódica
     * @see consumer_mqtt consumidor de mensajes de inicialización
    """
    print(f"   Datastream Service iniciando en {Config.HOST}:{Config.PORT}")
    print(f"   OSID: {Config.OSID}")
    print(f"   Title: {Config.TITLE}")
    
    # Configurar manejadores de señales para cierre seguro
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))
    
    #conectar_wifi()
    
    # Iniciar servidor
    server_task = asyncio.create_task(app.start_server(host=Config.HOST, port=Config.PORT))
    running_tasks.append(server_task)
    
    if Config.OSID:
        # Iniciar publicación periódica a ThingBoard si ya hay OSID y token        
        if Config.THINGSBOARD_ACCESS_TOKEN != "":
            global tb_publicacion_task
            print("Iniciando publicación a ThingsBoard...")
            tb_publicacion_task = asyncio.create_task(
                publicar_valores(tb_broker, Config.OSID, topic=Config.THINGSBOARD_TELEMETRY_TOPIC, interval=Config.TELEMETRY_PUBLISH_INTERVAL)
            )
            running_tasks.append(tb_publicacion_task)
        
        # Iniciar publicación periodica a Mosquitto si ya hay OSID
        global mosq_publicacion_task
        mosq_publicacion_task = asyncio.create_task(
            publicar_valores(mosquitto_broker, Config.OSID, topic=Config.MOSQUITTO_TELEMETRY_TOPIC, interval=Config.TELEMETRY_PUBLISH_INTERVAL)
        )
        running_tasks.append(mosq_publicacion_task)
    else:
        # Si el objeto no está inicializado, esperar a que se inicialice
        print("Esperando inicialización del objeto...")
        consumer_task = asyncio.create_task(consumer_mqtt(mosquitto_broker))
        running_tasks.append(consumer_task)
    
    # Esperar hasta que se solicite el cierre
    try:
        await shutdown_event.wait()
    except asyncio.CancelledError:
        pass


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor interrumpido por el usuario")