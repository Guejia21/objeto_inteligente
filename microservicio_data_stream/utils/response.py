import ujson as json
# from typing import Any, Dict, List, Optional  # typing no está disponible en MicroPython

class ResponseHelper:
    """Helper para crear respuestas JSON estandarizadas"""
    
    @staticmethod
    def success(data=None, message="Success", code="1000"):
        """Respuesta exitosa en JSON"""
        response = {
            "status": "success",
            "code": code,
            "message": message,
            "data": data if data is not None else {}
        }
        return json.dumps(response)
    
    @staticmethod
    def error(message="Error", code="1099", details=None):
        """Respuesta de error en JSON"""
        response = {
            "status": "error",
            "code": code,
            "message": message
        }
        if details:
            response["details"] = details
        
        return json.dumps(response)
    
    @staticmethod
    def simple_value(osid, variable, datatype, value):
        """Respuesta con valor simple de datastream"""
        response = {
            "osid": osid,
            "datastream": variable,
            "datatype": datatype,
            "value": value,
            "timestamp": ResponseHelper._get_timestamp()
        }
        return json.dumps(response,)
    
    @staticmethod
    def send_state_response(osid, datastreams):
        """Respuesta con estado de todos los datastreams"""
        response = {
            "osid": osid,
            "datastreams": datastreams,
            "timestamp": ResponseHelper._get_timestamp()
        }
        return json.dumps(response)
    
    @staticmethod
    def _get_timestamp():
        """Genera timestamp ISO 8601"""
        try:
            from time import time
            return str(int(time()))
        except:
            return "0"