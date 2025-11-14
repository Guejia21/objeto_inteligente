import os
import sys

class ModuleExecutor:
    """Ejecuta módulos Python para leer/escribir datastreams"""
    
    def __init__(self, path_ejecutables):
        self.path = path_ejecutables
    
    def get_value(self, datastream_id):
        """Obtiene el valor actual de un datastream (sensor)"""
        try:
            module_path = f"{self.path}get_{datastream_id}.py"            
            # En MicroPython no hay imp, usamos exec
            with open(module_path, 'r') as f:
                code = f.read()
            
            # Crear namespace para ejecutar el módulo
            namespace = {}
            exec(code, namespace)
            
            # Obtener el valor
            if 'value' in namespace:
                return str(namespace['value'])
            else:
                raise ValueError(f"Module {module_path} no tiene variable 'value'")
                
        except Exception as e:
            print(f"Error obteniendo valor de {datastream_id}: {e}")
            return "0"
    
    def set_value(self, datastream_id, comparador, valor):
        """Establece el valor de un datastream (actuador)"""
        try:
            module_path = f"{self.path}set_{datastream_id}.py"
            
            with open(module_path, 'r') as f:
                code = f.read()
            
            namespace = {'comparador': comparador, 'valor': valor}
            exec(code, namespace)
            
            # Ejecutar función main si existe
            if 'main' in namespace:
                namespace['main'](comparador, valor)
            
            return True
        except Exception as e:
            print(f"Error estableciendo valor de {datastream_id}: {e}")
            return False
    
    def execute_on_off(self, datastream_id, comando):
        """Ejecuta comandos on/off para actuadores"""
        try:
            if comando == "on":
                module_path = f"{self.path}on_{datastream_id}.py"
            elif comando == "off":
                module_path = f"{self.path}off_{datastream_id}.py"
            else:
                return False
            
            with open(module_path, 'r') as f:
                code = f.read()
            
            namespace = {}
            exec(code, namespace)
            
            if 'main' in namespace:
                namespace['main']()
            
            return True
        except Exception as e:
            print(f"Error ejecutando {comando} en {datastream_id}: {e}")
            return False