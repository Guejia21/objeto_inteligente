"""
Adaptador MQTT para MicroPython (ESP32)
Compatible con la interfaz de mqtt_adapter.py
"""

try:
    from lib.umqtt.simple import MQTTClient
    import ujson as json
    MICROPYTHON = True
except ImportError:
    # Fallback para testing en PC
    import json
    MICROPYTHON = False
    print("Ejecutando en modo PC (sin umqtt)")

import time
import gc

class MQTTMicroPythonAdapter:
    """Adaptador MQTT compatible con umqtt.simple"""
    
    def __init__(self, broker, port, client_id, username=None, password=None):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        self.subscriptions = {}
    
    def connect(self, retry=3):
        """Conecta al broker MQTT"""
        if not MICROPYTHON:
            print("MQTT simulado: " + self.broker + ":" + str(self.port))
            self.connected = True
            return True
        
        for attempt in range(retry):
            try:
                print("Intento MQTT " + str(attempt + 1) + "/" + str(retry))
                print("  Broker: " + self.broker + ":" + str(self.port))
                print("  Client ID: " + self.client_id)
                
                # ✅ Crear cliente con o sin credenciales según corresponda
                if self.username and self.password:
                    print("  User: " + self.username[:8] + "...")
                    self.client = MQTTClient(
                        client_id=self.client_id,
                        server=self.broker,
                        port=self.port,
                        user=self.username,
                        password=self.password,
                        keepalive=60
                    )
                elif self.username:
                    # Solo username (caso ThingsBoard)
                    print("  Token: " + self.username[:8] + "...")
                    self.client = MQTTClient(
                        client_id=self.client_id,
                        server=self.broker,
                        port=self.port,
                        user=self.username,
                        password="",  # String vacío en lugar de None
                        keepalive=60
                    )
                else:
                    # Sin credenciales
                    print("  Sin autenticacion")
                    self.client = MQTTClient(
                        client_id=self.client_id,
                        server=self.broker,
                        port=self.port,
                        keepalive=60
                    )
                
                # Conectar
                print("  Conectando...")
                self.client.connect()
                
                self.connected = True
                print("MQTT conectado OK: " + self.broker + ":" + str(self.port))
                
                # Liberar memoria
                gc.collect()
                
                return True
                
            except Exception as e:
                print("Intento " + str(attempt + 1) + "/" + str(retry) + " fallo: " + str(e))
                
                # Limpiar cliente fallido
                try:
                    if self.client:
                        self.client.disconnect()
                except:
                    pass
                self.client = None
                
                if attempt < retry - 1:
                    print("  Reintentando en 2s...")
                    time.sleep(2)
                
                gc.collect()
        
        print("No se pudo conectar a MQTT despues de " + str(retry) + " intentos")
        self.connected = False
        return False
    
    def publish(self, topic, payload, retain=False, qos=0):
        """Publica mensaje a MQTT"""
        if not MICROPYTHON:
            print("MQTT (sim) -> " + topic + ": " + str(payload))
            return True
        
        if not self.connected:
            print("MQTT no conectado, intentando reconectar...")
            if not self.connect():
                return False
        
        try:
            # Convertir payload a bytes
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            if isinstance(payload, str):
                payload = payload.encode()
            
            # Publicar
            self.client.publish(topic, payload, retain=retain, qos=qos)
            
            print("MQTT publicado: " + topic)
            return True
            
        except Exception as e:
            print("Error publicando MQTT: " + str(e))
            self.connected = False
            return False
    
    def subscribe(self, topic, callback=None):
        """Suscribe a un tópico"""
        if not MICROPYTHON:
            print("MQTT (sim) suscrito: " + topic)
            return True
        
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            self.subscriptions[topic] = callback
            
            def message_handler(topic_bytes, msg_bytes):
                topic_str = topic_bytes.decode()
                msg_str = msg_bytes.decode()
                
                print("MQTT mensaje recibido: " + topic_str)
                
                # Llamar callback si existe
                cb = self.subscriptions.get(topic_str)
                if cb:
                    try:
                        cb(topic_str, msg_str)
                    except Exception as e:
                        print("Error en callback: " + str(e))
            
            self.client.set_callback(message_handler)
            self.client.subscribe(topic)
            print("MQTT suscrito: " + topic)
            return True
            
        except Exception as e:
            print("Error suscribiendo: " + str(e))
            return False
    
    def check_msg(self):
        """Verifica mensajes pendientes (non-blocking)"""
        if MICROPYTHON and self.client and self.connected:
            try:
                self.client.check_msg()
            except Exception as e:
                print("Error verificando mensajes: " + str(e))
    
    def disconnect(self):
        """Desconecta del broker"""
        if MICROPYTHON and self.client and self.connected:
            try:
                self.client.disconnect()
                print("MQTT desconectado")
            except:
                pass
        
        self.client = None
        self.connected = False
        gc.collect()


# ✅ NO crear instancias globales aquí (causan error en import)
# Se crean bajo demanda en telemetry_service.py o donde se necesiten