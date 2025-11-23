from lib.microdot.microdot import Request, Response
from services.datastream_service import DatastreamService
import json as json
# Instancia del servicio
datastream_service = DatastreamService()

def register_routes(app):
    """Registra las rutas en la aplicación Microdot"""    
    @app.route('/Datastreams/SendState', methods=['GET'])
    @app.route('/Datastreams/SendState/', methods=['GET'])
    async def send_state(request: Request):
        """
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
    
    @app.route('/Datastreams/SetDatastream', methods=['GET'])
    @app.route('/Datastreams/SetDatastream/', methods=['GET'])
    async def set_datastream(request: Request):
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