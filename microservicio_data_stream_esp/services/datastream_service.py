"""
Servicio de Datastreams
Ejecuta scripts de hardware y genera respuestas JSON
"""

try:
    import ujson as json
except ImportError:
    import json

from storage.metadata.metadata import obtener_metadatos, obtener_datastream
from config import Config
from utils.response import ResponseFormatter

# Importar hardware adapter según plataforma
try:
    from hardware.esp32_hw_adapter import hw_adapter
    USE_HW_ADAPTER = True
    print("Usando ESP32 Hardware Adapter")
except ImportError:
    from utils.module_executor import ModuleExecutor
    USE_HW_ADAPTER = False
    print("Usando ModuleExecutor (modo PC)")


class DatastreamService:
    """Servicio para gestión de datastreams"""
    
    def __init__(self):
        self.metadata = obtener_metadatos()
        self.datastreams = self.metadata.get('datastreams', [])
        self.response = ResponseFormatter()
        
        # Inicializar executor solo en modo PC
        if not USE_HW_ADAPTER:
            self.executor = ModuleExecutor("default")
        
        # ✅ SIN f-string
        print("DatastreamService inicializado (" + str(len(self.datastreams)) + " datastreams)")
    
    # ===== MÉTODOS AUXILIARES =====
    
    def get_datastreams(self):
        """Obtiene lista de todos los datastreams"""
        return self.datastreams
    
    def datastream_exists(self, datastream_id):
        """Verifica si un datastream existe"""
        return any(ds['datastream_id'] == datastream_id for ds in self.datastreams)
    
    def get_datastream_info(self, datastream_id):
        """Obtiene información completa de un datastream"""
        return obtener_datastream(datastream_id)
    
    # ===== EJECUCIÓN DE ACCIONES =====
    
    def execute_datastream_action(self, datastream_id, action, params=None):
        """
        Ejecuta una acción sobre un datastream
        Args:
            datastream_id: ID del datastream (ej: 'led_status', 'rtc_time')
            action: Acción a ejecutar (ej: 'on', 'off', 'get')
            params: Parámetros adicionales (dict)
        Returns:
            dict: Resultado de la ejecución
        """
        # Validar acción
        valid_actions = ['on', 'off', 'get', 'set']
        if action not in valid_actions:
            return {'success': False, 'error': 'Accion no soportada: ' + action}
        
        # Verificar que el datastream existe
        ds_info = self.get_datastream_info(datastream_id)
        if not ds_info:
            return {'success': False, 'error': 'Datastream no encontrado: ' + datastream_id}
        
        # Determinar script a ejecutar
        script_name = action + "_" + datastream_id + ".py"
        script_path = "storage/executables/" + script_name
        
        print("Ejecutando: " + script_path)
        
        # Ejecutar según plataforma
        if USE_HW_ADAPTER:
            # ESP32: Usar hardware adapter
            result = hw_adapter.execute_script(script_path, params)
        else:
            # PC: Usar ModuleExecutor
            try:
                if action == "on":
                    success = self.executor.execute_on_off(datastream_id, "on")
                    result = {'success': success, 'value': True}
                elif action == "off":
                    success = self.executor.execute_on_off(datastream_id, "off")
                    result = {'success': success, 'value': False}
                elif action == "get":
                    value = self.executor.get_value(datastream_id)
                    result = {'success': True, 'value': value}
                elif action == "set":
                    value = params.get('value') if params else None
                    success = self.executor.set_value(datastream_id, "igual", value)
                    result = {'success': success, 'value': value}
                else:
                    result = {'success': False, 'error': 'Accion no implementada en PC'}
            except Exception as e:
                result = {'success': False, 'error': str(e)}
        
        return result
    
    def get_datastream_value(self, datastream_id):
        """
        Obtiene el valor actual de un datastream
        Args:
            datastream_id: ID del datastream
        Returns:
            Valor actual o "0" si hay error
        """
        try:
            result = self.execute_datastream_action(datastream_id, 'get')
            
            if result.get('success'):
                value = result.get('value')
                
                # Si el valor es un dict con 'readable', usar ese
                if isinstance(value, dict) and 'readable' in value:
                    return value['readable']
                
                # Si es booleano, convertir a string
                if isinstance(value, bool):
                    return "true" if value else "false"
                
                return str(value)
            else:
                print("Error obteniendo valor de " + datastream_id + ": " + str(result.get('error')))
                return "0"
                
        except Exception as e:
            print("Error en get_datastream_value(" + datastream_id + "): " + str(e))
            return "0"
    
    def get_datastreams_values(self):
        """
        Obtiene valores actuales de todos los datastreams
        Returns:
            list: Lista de datastreams con sus valores actuales
        """
        results = []
        
        for ds in self.datastreams:
            ds_id = ds.get('datastream_id')
            
            # Obtener valor
            value = self.get_datastream_value(ds_id)
            
            result_item = {
                'datastream_id': ds_id,
                'current_value': value
            }
            result_item.update(ds)
            results.append(result_item)
        
        return results
    
    # ===== ENDPOINTS DEL SERVICIO =====
    
    def send_data(self, osid, variable_estado, tipove):
        """
        Envía datos de un datastream específico
        
        Args:
            osid: ID del objeto
            variable_estado: ID del datastream
            tipove: Tipo (1=propiedad de interés)
        
        Returns:
            JSON con el valor del datastream
        """
        # Validar OSID
        if Config.OSID != osid:
            return self.response.error(
                "ID incorrecto",
                Config.CODES['idIncorrecto']
            )
        
        # Validar tipo
        if int(tipove) != 1:
            return self.response.error(
                "Tipo no implementado",
                Config.CODES['noImplementado']
            )
        
        # Verificar que el datastream existe
        if not self.datastream_exists(variable_estado):
            return self.response.error(
                "Datastream '" + variable_estado + "' no existe",
                Config.CODES['dataStremNoExiste']
            )
        
        try:
            # Obtener información del datastream
            ds_info = self.get_datastream_info(variable_estado)
            datastream_format = ds_info.get('datastream_format', 'string')
            
            # Obtener valor actual
            value = self.get_datastream_value(variable_estado)
            
            print("SendData: " + variable_estado + " = " + str(value))
            
            # Retornar JSON con el valor
            return self.response.simple_value(
                osid, 
                variable_estado, 
                datastream_format, 
                value
            )
            
        except Exception as e:
            print("Error en send_data: " + str(e))
            return self.response.error(
                "Error obteniendo datos: " + str(e),
                Config.CODES['errorDatastream'],
                str(e)
            )
    
    def send_state(self, osid):
        """
        Envía el estado de todos los datastreams
        
        Args:
            osid: ID del objeto
        
        Returns:
            JSON con el estado de todos los datastreams
        """
        # Validar OSID
        if Config.OSID != osid:
            return self.response.error(
                "ID incorrecto",
                Config.CODES['idIncorrecto']
            )
        
        try:
            datastreams_state = []
            
            # Obtener valor de cada datastream
            for ds in self.datastreams:
                ds_id = ds['datastream_id']
                ds_format = ds.get('datastream_format', 'string')
                ds_type = ds.get('datastream_type', 'sensor')
                
                # Obtener valor
                value = self.get_datastream_value(ds_id)
                
                datastreams_state.append({
                    "datastream_id": ds_id,
                    "datastream_format": ds_format,
                    "datastream_type": ds_type,
                    "value": value
                })
            
            print("SendState: " + str(len(datastreams_state)) + " datastreams")
            
            return self.response.send_state_response(osid, datastreams_state)
            
        except Exception as e:
            print("Error en send_state: " + str(e))
            return self.response.error(
                "Error obteniendo estado: " + str(e),
                Config.CODES['errorAbrirArchivo'],
                str(e)
            )
    
    def set_datastream(self, osid, id_datastream, comando):
        """
        Establece el valor de un datastream (actuador)
        
        Args:
            osid: ID del objeto
            id_datastream: ID del datastream
            comando: Comando (on/off/valor)
        
        Returns:
            JSON con resultado de la operación
        """
        # Validar OSID
        if Config.OSID != osid:
            return self.response.error(
                "ID incorrecto",
                Config.CODES['idIncorrecto']
            )
        
        # Verificar que el datastream existe
        if not self.datastream_exists(id_datastream):
            return self.response.error(
                "Datastream '" + id_datastream + "' no existe",
                Config.CODES['dataStremNoExiste']
            )
        
        try:
            print("SetDatastream: " + id_datastream + " -> " + comando)
            
            result = None
            
            # Ejecutar comando según el tipo
            if comando.lower() == "on":
                result = self.execute_datastream_action(id_datastream, "on")
            elif comando.lower() == "off":
                result = self.execute_datastream_action(id_datastream, "off")
            else:
                # Comando con valor (para datastreams numéricos o set)
                result = self.execute_datastream_action(
                    id_datastream, 
                    "set",
                    params={'value': comando}
                )
            
            # Verificar resultado
            if result and result.get('success'):
                print("Comando ejecutado: " + id_datastream + " -> " + comando)
                
                return self.response.success(
                    data={
                        "datastream_id": id_datastream,
                        "comando": comando,
                        "applied": True,
                        "value": result.get('value')
                    },
                    message="Datastream '" + id_datastream + "' actualizado a '" + comando + "'",
                    code=Config.CODES['datastreamEncendido']
                )
            else:
                error_msg = result.get('error', 'Error desconocido') if result else 'Sin respuesta'
                print("Error ejecutando comando: " + error_msg)
                
                return self.response.error(
                    "Error ejecutando comando: " + error_msg,
                    Config.CODES['errorDatastream']
                )
                
        except Exception as e:
            print("Error en set_datastream: " + str(e))
            import sys
            if hasattr(sys, 'print_exception'):
                sys.print_exception(e)
            
            return self.response.error(
                "Error estableciendo datastream: " + str(e),
                Config.CODES['errorDatastream'],
                str(e)
            )