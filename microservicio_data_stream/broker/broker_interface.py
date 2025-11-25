"""Interface para el broker de mensajería (por ejemplo, MQTT)"""

from routes.datastreams import datastream_service
import asyncio
from utils import util
import json
from config import Config
from main import publicacion_task
class BrokerInterface:
    async def publicar(self, topico, mensaje):
        raise NotImplementedError("Debe implementar 'publicar'")

    async def suscribirse(self, topico, callback):
        raise NotImplementedError("Debe implementar 'suscribirse'")

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
    # Capturamos el loop principal aquí, antes de entrar al callback del hilo
    loop = asyncio.get_running_loop()
    
    def recibir_datastreams(topic, msg):
        # Esta función corre en un hilo separado (creado por paho-mqtt)
        # Debemos delegar la ejecución al loop principal de asyncio
        
        async def procesar_logica():
            global publicacion_task
            print("Registrando datastream desde mensaje MQTT...")
            try:
                datastreams = util.convert_metadata_format(json.loads(msg))
                util.save_metadata(datastreams)
                util.create_executables(datastreams["datastreams"], datastreams["object"]["id"])
                datastream_service._load_metadata()
                print("Datastreams registrados correctamente.")
                print("Por favor, cargue los ejecutables pertinentes y reinicie este servicio si es necesario.")
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
            except Exception as e:
                print(f"Error al procesar datastreams: {e}")

        # Usamos run_coroutine_threadsafe para enviar la corrutina al loop principal
        asyncio.run_coroutine_threadsafe(procesar_logica(), loop)

    await broker.suscribirse(Config.REGISTER_DATASTREAMS_QUEUE_NAME, recibir_datastreams)
