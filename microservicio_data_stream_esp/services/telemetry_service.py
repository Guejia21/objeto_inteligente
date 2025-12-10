"""
Servicio de Telemetría para ThingsBoard
Publica valores de datastreams periódicamente
"""

try:
    import ujson as json
except ImportError:
    import json

import time
import gc
from config import Config

class TelemetryService:
    """Gestiona publicación de telemetría a ThingsBoard"""
    
    def __init__(self, datastream_service, mqtt_client):
        self.datastream_service = datastream_service
        self.mqtt_client = mqtt_client
        self.last_publish = 0
        self.enabled = Config.TELEMETRY_ENABLED
        self.interval = Config.TELEMETRY_INTERVAL
        self.connected = False
        
        print("TelemetryService inicializado")
        print("  Intervalo: " + str(self.interval) + "s")
        print("  Habilitado: " + str(self.enabled))
    
    def connect(self):
        """Conecta al broker MQTT de ThingsBoard"""
        if self.connected:
            return True
        
        try:
            print("\nConectando a ThingsBoard MQTT...")
            print("  Broker: " + Config.THINGSBOARD_HOST + ":" + str(Config.THINGSBOARD_PORT))
            print("  Token: " + Config.THINGSBOARD_ACCESS_TOKEN[:8] + "...")
            
            if self.mqtt_client.connect(retry=3):
                self.connected = True
                print("ThingsBoard MQTT conectado!")
                return True
            else:
                print("No se pudo conectar a ThingsBoard")
                return False
                
        except Exception as e:
            print("Error conectando ThingsBoard: " + str(e))
            return False
    
    def collect_telemetry(self):
        """
        Recolecta valores actuales de todos los datastreams
        Returns:
            dict: Telemetría en formato ThingsBoard
        """
        telemetry = {}
        
        try:
            # Obtener todos los datastreams
            datastreams = self.datastream_service.get_datastreams()
            
            for ds in datastreams:
                ds_id = ds.get('datastream_id')
                ds_type = ds.get('datastream_type', 'sensor')
                
                # Obtener valor actual
                value = self.datastream_service.get_datastream_value(ds_id)
                
                # Convertir a tipo apropiado
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                elif value.replace('.', '', 1).replace('-', '', 1).isdigit():
                    # Es numérico
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                
                # Agregar a telemetría
                telemetry[ds_id] = value
            
            # Agregar metadata adicional                        
            telemetry['_mem_free'] = gc.mem_free()
            
            return telemetry
            
        except Exception as e:
            print("Error recolectando telemetria: " + str(e))
            return {}
    
    def publish_telemetry(self, telemetry=None):
        """
        Publica telemetría a ThingsBoard
        Args:
            telemetry: Dict con datos. Si None, recolecta automáticamente
        Returns:
            bool: True si publicó exitosamente
        """
        if not self.enabled:
            return False
        
        # Conectar si no está conectado
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            # Recolectar telemetría si no se proporcionó
            if telemetry is None:
                telemetry = self.collect_telemetry()
            
            if not telemetry:
                print("No hay telemetria para publicar")
                return False
            
            # Convertir a JSON
            payload = json.dumps(telemetry)
            
            # Publicar a ThingsBoard
            topic = Config.THINGSBOARD_TELEMETRY_TOPIC
            
            print("\nPublicando telemetria a ThingsBoard:")
            print("  Topic: " + topic)
            print("  Payload: " + payload)
            
            success = self.mqtt_client.publish(topic, payload, qos=1)
            
            if success:
                print("Telemetria publicada OK")
                self.last_publish = time.time()
                return True
            else:
                print("Error publicando telemetria")
                self.connected = False
                return False
                
        except Exception as e:
            print("Error en publish_telemetry: " + str(e))
            import sys
            if hasattr(sys, 'print_exception'):
                sys.print_exception(e)
            
            self.connected = False
            return False
    
    def should_publish(self):
        """Verifica si es momento de publicar telemetría"""
        if not self.enabled:
            return False
        
        now = time.time()
        elapsed = now - self.last_publish
        
        return elapsed >= self.interval
    
    def loop(self):
        """
        Loop principal de telemetría (llamar periódicamente)
        Publica si ha pasado el intervalo
        """
        if self.should_publish():
            print("\n=== Loop de Telemetria ===")
            self.publish_telemetry()
            
            # Liberar memoria
            gc.collect()
            print("Memoria libre: " + str(gc.mem_free()) + " bytes")
    
    def disconnect(self):
        """Desconecta del broker MQTT"""
        if self.mqtt_client and self.connected:
            try:
                self.mqtt_client.disconnect()
                print("ThingsBoard MQTT desconectado")
            except:
                pass
        
        self.connected = False