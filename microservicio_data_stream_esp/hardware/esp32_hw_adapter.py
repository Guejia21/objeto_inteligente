"""
Adaptador de hardware para ESP32 - Optimizado para memoria
"""

try:
    from machine import Pin, RTC
    import time
    MICROPYTHON = True
except ImportError:
    MICROPYTHON = False
    import time

import gc

class ESP32HardwareAdapter:
    """Ejecuta scripts de hardware en ESP32"""
    
    def __init__(self):
        self.platform = "ESP32" if MICROPYTHON else "PC"
        self.pins = {}  # Compartido entre todos los scripts
        
        # Liberar memoria
        gc.collect()
        print("Hardware adapter inicializado (" + self.platform + ")")
    
    def execute_script(self, script_path, params=None):
        """Ejecuta un script Python con parámetros"""
        if params is None:
            params = {}
        
        # Liberar memoria antes de ejecutar
        gc.collect()
        
        try:
            # Leer script
            with open(script_path, 'r') as f:
                script_code = f.read()
            
            # Namespace mínimo
            namespace = {
                'Pin': Pin if MICROPYTHON else None,
                'RTC': RTC if MICROPYTHON else None,
                'time': time,
                'pins': self.pins,
                'params': params,
                'result': None,
            }
            
            # Ejecutar
            exec(script_code, namespace)
            
            # Obtener resultado
            result = namespace.get('result', {'success': True})
            
            # Liberar namespace
            del namespace
            gc.collect()
            
            return result
            
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'FileNotFoundError',
                'message': 'Script no encontrado: ' + script_path
            }
        
        except Exception as e:
            print("Error ejecutando " + script_path + ": " + str(e))
            return {
                'success': False,
                'error': type(e).__name__,
                'message': str(e)
            }
    
    def cleanup(self):
        """Limpia recursos"""
        for pin_name, pin_obj in self.pins.items():
            try:
                if MICROPYTHON and hasattr(pin_obj, 'value'):
                    pin_obj.value(0)
            except:
                pass
        
        self.pins.clear()
        gc.collect()


# Instancia global
hw_adapter = ESP32HardwareAdapter()