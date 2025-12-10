"""
@file datastreams.py
@brief Definición de rutas HTTP para gestión de datastreams
@details
Registra endpoints Microdot para:
- Obtener estado de todos los datastreams (SendState)
- Obtener valor de un datastream específico (SendData)
- Establecer valor en un actuador (SetDatastream)

Parámetros principales:
- osid: ID del objeto inteligente (requerido en todos)
- variableEstado: ID del datastream (requerido en SendData/SetDatastream)
- tipove: Tipo de variable (1=propiedad de interés)
- comando: Valor a establecer en actuador

@see main.py donde se llama register_routes()
@see services/datastream_service.py para lógica de negocio

@author Sistema de Objetos Inteligentes
@version 1.0.0
"""

from lib.microdot.microdot import Request, Response
from services.datastream_service import DatastreamService
import json as json
# Instancia del servicio
datastream_service = DatastreamService()

def register_routes(app):
    """
    @brief Registra todas las rutas de datastreams en la aplicación Microdot
    @param app Microdot - Instancia de aplicación Microdot
    @return void
    
    Rutas registradas:
    - GET /Datastreams/SendState
    - GET /Datastreams/SendData
    - POST /Datastreams/SetDatastream
    """    
    @app.route('/Datastreams/SendState', methods=['GET'])
    @app.route('/Datastreams/SendState/', methods=['GET'])
    async def send_state(request: Request):
        """
         * @brief GET /Datastreams/SendState - Obtiene estado de todos los datastreams
         * @details
         * Retorna el estado completo (valores) de todos los datastreams
         * configurados en metadata.json
         * 
         * @param request Request - Objeto de solicitud Microdot
         *        request.args.get('osid') - ID del objeto inteligente (requerido)
         * 
         * @return Response JSON con:
         *         {
         *           "status": "ok|error",
         *           "osid": "<id>",
         *           "datastreams": [
         *             {"id": "temp", "value": 25.5, "type": "float"},
         *             ...
         *           ]
         *         }
         * @status 400 - Si osid no se proporciona
         * @status 500 - Error interno del servicio
         * 
         * @see DatastreamService.send_state()
         */
        Endpoint: /Datastreams/SendState?osid=<id>
        Obtiene el estado de todos los datastreams
        """
        try:
            osid = request.args.get('osid')
            
            if not osid:
                return Response(
                    '{"status":"error","message":"Parámetro osid faltante"}',
                    status_code=400,
                    headers={'Content-Type': 'application/json'}
                )
            print("Enviando SendState")
            result = datastream_service.send_state(osid)
            print(f"SendState exitoso")
            return Response(
                result,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
        except Exception as e:
            return Response(
                f'{{"status":"error","message":"{str(e)}"}}',
                status_code=500,
                headers={'Content-Type': 'application/json'}
            )
    
    @app.route('/Datastreams/SendData', methods=['GET'])
    @app.route('/Datastreams/SendData/', methods=['GET'])
    async def send_data(request: Request):
        """
         * @brief GET /Datastreams/SendData - Obtiene valor de datastream específico
         * @details
         * Retorna el valor actual de un datastream (sensor o variable de estado).
         * Ejemplo de uso: /Datastreams/SendData?osid=ESP32_Sala&variableEstado=temperatura&tipove=1
         * 
         * @param request Request - Objeto de solicitud Microdot
         *        request.args.get('osid') - ID del objeto inteligente (requerido)
         *        request.args.get('variableEstado') - ID del datastream (requerido)
         *        request.args.get('tipove') - Tipo de variable, default=1 (propiedad de interés)
         * 
         * @return Response JSON con:
         *         {
         *           "status": "ok",
         *           "osid": "<id>",
         *           "datastream_id": "temperatura",
         *           "value": 25.5,
         *           "datastream_format": "float"
         *         }
         * @status 400 - Si osid o variableEstado no se proporcionan
         * @status 500 - Error interno del servicio
         * 
         * @see DatastreamService.send_data()
         */

        Endpoint: /Datastreams/SendData?osid=<id>&variableEstado=<var>&tipove=<tipo>
        Ejemplo: /Datastreams/SendData?osid=ESP32_Sala&variableEstado=temperatura&tipove=1
        Obtiene el valor actual de un datastream específico
        """
        try:
            osid = request.args.get('osid')
            variable_estado = request.args.get('variableEstado')
            tipo_ve = request.args.get('tipove', '1')
            
            if not osid or not variable_estado:
                return Response(
                    '{"status":"error","message":"Parámetros faltantes"}',
                    status_code=400,
                    headers={'Content-Type': 'application/json'}
                )
            
            result = datastream_service.send_data(osid, variable_estado, tipo_ve)
            
            return Response(
                result,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
        except Exception as e:
            return Response(
                f'{{"status":"error","message":"{str(e)}"}}',
                status_code=500,
                headers={'Content-Type': 'application/json'}
            )
    
    @app.route('/Datastreams/SetDatastream', methods=['POST'])
    @app.route('/Datastreams/SetDatastream/', methods=['POST'])
    async def set_datastream(request: Request):
        """
         * @brief POST /Datastreams/SetDatastream - Establece valor en actuador
         * @details
         * Envía comando a un actuador (datastream escribible).
         * Ejemplo: /Datastreams/SetDatastream?osid=ESP32_Sala&idDataStream=lampara&comando=on
         * 
         * @param request Request - Objeto de solicitud Microdot
         *        request.args.get('osid') - ID del objeto inteligente (requerido)
         *        request.args.get('idDataStream') - ID del actuador (requerido)
         *        request.args.get('comando') - Comando a ejecutar (requerido)
         * 
         * @return Response JSON con:
         *         {
         *           "status": "ok|error",
         *           "message": "Comando ejecutado correctamente",
         *           "datastream_id": "lampara",
         *           "command": "on"
         *         }
         * @status 400 - Si faltan parámetros
         * @status 500 - Error interno del servicio
         * 
         * @see DatastreamService.set_datastream()
         """
        """
        Endpoint: /Datastreams/SetDatastream?osid=<id>&idDataStream=<ds>&comando=<cmd>
        Establece el valor de un datastream (actuador)
        """
        try:
            osid = request.args.get('osid')
            id_datastream = request.args.get('idDataStream')
            comando = request.args.get('comando')
            
            if not osid or not id_datastream or not comando:
                return Response(
                    '{"status":"error","message":"Parámetros faltantes"}',
                    status_code=400,
                    headers={'Content-Type': 'application/json'}
                )
            
            result = datastream_service.set_datastream(osid, id_datastream, comando)
            
            return Response(
                result,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
        except Exception as e:
            return Response(
                f'{{"status":"error","message":"{str(e)}"}}',
                status_code=500,
                headers={'Content-Type': 'application/json'}
            )
    
    @app.route('/Datastreams/health', methods=['GET'])
    async def health_check(request: Request):
        """Health check endpoint"""
        from config import Config
        return Response(
            json.dumps({
                "status": "healthy",
                "service": "datastream",
                "osid": Config.OSID,
                "title": Config.TITLE
            }),
            headers={'Content-Type': 'application/json'}
        )