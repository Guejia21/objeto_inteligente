"""
Formateador de respuestas JSON para el microservicio
Compatible con MicroPython
"""

try:
    import ujson as json
except ImportError:
    import json


class ResponseFormatter:
    """Genera respuestas JSON estandarizadas"""
    
    def success(self, data=None, message="OK", code=200):
        """
        Genera respuesta exitosa
        Args:
            data: Datos a retornar
            message: Mensaje descriptivo
            code: Código de respuesta
        """
        response = {
            "status": "success",
            "code": code,
            "message": message
        }
        
        if data is not None:
            response["data"] = data
        
        return json.dumps(response)
    
    def error(self, message, code=500, details=None):
        """
        Genera respuesta de error
        Args:
            message: Mensaje de error
            code: Código de error
            details: Detalles adicionales
        """
        response = {
            "status": "error",
            "code": code,
            "message": message
        }
        
        if details is not None:
            response["details"] = details
        
        return json.dumps(response)
    
    def simple_value(self, osid, datastream_id, datastream_format, value):
        """
        Genera respuesta simple con un valor de datastream
        Args:
            osid: ID del objeto
            datastream_id: ID del datastream
            datastream_format: Formato del datastream
            value: Valor actual
        """
        response = {
            "osid": osid,
            "datastream_id": datastream_id,
            "datastream_format": datastream_format,
            "value": value
        }
        
        return json.dumps(response)
    
    def send_state_response(self, osid, datastreams):
        """
        Genera respuesta para SendState
        Args:
            osid: ID del objeto
            datastreams: Lista de datastreams con sus valores
        """
        response = {
            "osid": osid,
            "datastreams": datastreams,
            "count": len(datastreams)
        }
        
        return json.dumps(response)