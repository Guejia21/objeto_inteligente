import json as json
from utils.module_executor import ModuleExecutor
from utils.response import ResponseHelper
from config import Config

class DatastreamService:
    """Servicio para gestionar datastreams"""
    
    def __init__(self):
        self.executor = ModuleExecutor(Config.PATH_EJECUTABLES)
        self.response = ResponseHelper()
        self._load_metadata()
    
    def _load_metadata(self):
        """Carga metadata del objeto desde JSON"""
        try:
            with open(f"{Config.PATH_METADATA}metadata.json", 'r') as f:
                metadata = json.load(f)
                Config.OSID = metadata['object']['id']
                Config.TITLE = metadata['object'].get('title', 'Unknown')
                Config.OBJECT_IP = metadata['object'].get('ip_object', 'Unknown')
                Config.THINGSBOARD_TOKEN = metadata['object'].get('thingsboard_token', '')
                self.datastreams = metadata.get('datastreams', [])
                print(f"Metadata cargada: OSID={Config.OSID}, Datastreams={len(self.datastreams)}")
        except Exception as e:
            print(f"Error cargando metadata: {e}")
            self.datastreams = []
    
    def datastream_exists(self, datastream_id):
        """Verifica si un datastream existe"""
        return any(ds['datastream_id'] == datastream_id for ds in self.datastreams)
    
    def get_datastream_info(self, datastream_id):
        """Obtiene información completa de un datastream"""
        for ds in self.datastreams:
            if ds['datastream_id'] == datastream_id:
                return ds
        return None
    
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
                f"Datastream '{variable_estado}' no existe",
                Config.CODES['dataStremNoExiste']
            )
        
        try:
            # Obtener información del datastream
            ds_info = self.get_datastream_info(variable_estado)
            datastream_format = ds_info.get('datastream_format', 'string')
            
            # Obtener valor actual
            value = self.executor.get_value(variable_estado)
            
            print(f"SendData: {variable_estado} = {value}")
            
            # Retornar JSON con el valor
            return self.response.simple_value(
                osid, 
                variable_estado, 
                datastream_format, 
                value
            )
            
        except Exception as e:
            return self.response.error(
                f"Error obteniendo datos: {str(e)}",
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
                
                try:
                    value = self.executor.get_value(ds_id)
                except Exception as e:
                    print(f"Error obteniendo valor de {ds_id}: {e}")
                    value = "0"
                
                datastreams_state.append({
                    "datastream_id": ds_id,
                    "datastream_format": ds_format,
                    "datastream_type": ds_type,
                    "value": value
                })
                        
            return self.response.send_state_response(osid, datastreams_state)
            
        except Exception as e:
            return self.response.error(
                f"Error obteniendo estado: {str(e)}",
                Config.CODES['errorAbrirArchivo'],
                str(e)
            )
    
    def set_datastream(self, osid, id_datastream, comando):
        """
        Establece el valor de un datastream (actuador)
        
        Args:
            osid: ID del objeto
            id_datastream: ID del datastream
            comando: Comando (on/off/valor numérico)
        
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
                f"Datastream '{id_datastream}' no existe",
                Config.CODES['dataStremNoExiste']
            )
        
        try:
            print(f"SetDatastream: {id_datastream} -> {comando}")
            
            success = False
            
            # Ejecutar comando según el tipo
            if comando.lower() == "on":
                success = self.executor.execute_on_off(id_datastream, "on")
            elif comando.lower() == "off":
                success = self.executor.execute_on_off(id_datastream, "off")
            else:
                # Comando con valor numérico
                success = self.executor.set_value(
                    id_datastream, 
                    "igual",  # Comparador por defecto
                    comando
                )
            
            if success:
                return self.response.success(
                    data={
                        "datastream_id": id_datastream,
                        "comando": comando,
                        "applied": True
                    },
                    message=f"Datastream '{id_datastream}' actualizado a '{comando}'",
                    code=Config.CODES['datastreamEncendido']
                )
            else:
                return self.response.error(
                    "Error ejecutando comando",
                    Config.CODES['errorDatastream']
                )
                
        except Exception as e:
            return self.response.error(
                f"Error estableciendo datastream: {str(e)}",
                Config.CODES['errorDatastream'],
                str(e)
            )        
