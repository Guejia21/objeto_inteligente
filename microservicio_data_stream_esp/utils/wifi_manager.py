"""
Gestor de WiFi para ESP32 - Compatible y robusto
"""

import network
import time
import gc

class WiFiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = None
        self.connected = False
    
    def connect(self, timeout=20):
        """Conecta al WiFi"""
        if self.connected and self.wlan and self.wlan.isconnected():
            print("WiFi ya conectado")
            return True
        
        # Liberar memoria antes
        gc.collect()
        print("Memoria antes de WiFi: " + str(gc.mem_free()))
        
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            
            # Esperar a que WiFi se active
            time.sleep(0.5)
            
            # ✅ CONFIGURAR POWER SAVE (método compatible)
            try:
                # Intentar desactivar power save (puede fallar en algunas versiones)
                self.wlan.config(pm=network.WLAN.PM_NONE)
                print("Power Save: DESACTIVADO")
            except:
                # Si falla, continuar sin power save config
                print("Power Save: No configurable (continuando...)")
            
            if not self.wlan.isconnected():
                print("Conectando a WiFi: " + self.ssid)
                self.wlan.connect(self.ssid, self.password)
                
                # Esperar conexión con feedback
                retry = 0
                max_retry = timeout * 2
                
                while not self.wlan.isconnected() and retry < max_retry:
                    if retry % 4 == 0:  # Cada 2 segundos
                        print("  Intentando conectar... (" + str(retry // 2) + "s)")
                    time.sleep(0.5)
                    retry += 1
                
                if self.wlan.isconnected():
                    config = self.wlan.ifconfig()
                    ip = config[0]
                    netmask = config[1]
                    gateway = config[2]
                    dns = config[3]
                    
                    print("\n=== WiFi CONECTADO ===")
                    print("  IP:      " + ip)
                    print("  Netmask: " + netmask)
                    print("  Gateway: " + gateway)
                    print("  DNS:     " + dns)
                    print("======================\n")
                    
                    self.connected = True
                    
                    # Liberar memoria después
                    gc.collect()
                    print("Memoria despues de WiFi: " + str(gc.mem_free()))
                    
                    return True
                else:
                    print("\nWiFi: Timeout despues de " + str(timeout) + "s")
                    self.disconnect()
                    return False
            else:
                print("WiFi: Ya estaba conectado")
                self.connected = True
                return True
            
        except Exception as e:
            print("\nError conectando WiFi: " + str(e))
            import sys
            if hasattr(sys, 'print_exception'):
                sys.print_exception(e)
            
            # Intentar limpiar
            try:
                if self.wlan:
                    self.wlan.active(False)
            except:
                pass
            
            self.wlan = None
            self.connected = False
            return False
    
    def keep_alive(self):
        """Verifica y reconecta si es necesario"""
        try:
            if not self.wlan:
                print("WiFi no inicializado - Reconectando...")
                return self.connect()
            
            if not self.wlan.isconnected():
                print("WiFi desconectado - Reconectando...")
                self.connected = False
                return self.connect()
            
            # WiFi OK
            return True
            
        except Exception as e:
            print("Error en keep_alive: " + str(e))
            return False
    
    def disconnect(self):
        """Desconecta del WiFi y libera memoria"""
        try:
            if self.wlan:
                if self.wlan.isconnected():
                    self.wlan.disconnect()
                self.wlan.active(False)
                time.sleep(0.5)
                self.wlan = None
                print("WiFi desconectado")
        except Exception as e:
            print("Error desconectando: " + str(e))
        
        self.connected = False
        gc.collect()
    
    def get_ip(self):
        """Obtiene IP actual"""
        try:
            if self.wlan and self.wlan.isconnected():
                return self.wlan.ifconfig()[0]
        except:
            pass
        return None
    
    def get_info(self):
        """Obtiene información completa de la conexión"""
        if not self.wlan or not self.wlan.isconnected():
            return None
        
        try:
            config = self.wlan.ifconfig()
            return {
                "ip": config[0],
                "netmask": config[1],
                "gateway": config[2],
                "dns": config[3],
                "connected": True
            }
        except:
            return None
    
    def status(self):
        """Obtiene status de conexión (string legible)"""
        if not self.wlan:
            return "WiFi no inicializado"
        
        try:
            if self.wlan.isconnected():
                ip = self.wlan.ifconfig()[0]
                return "Conectado - IP: " + ip
            else:
                return "Desconectado"
        except:
            return "Error obteniendo status"


# Instancia global (NO conecta automáticamente)
wifi_manager = WiFiManager(
    ssid="NexTech",
    password="nextechOI"
)