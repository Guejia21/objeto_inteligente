from fastapi import Request, Response
from app.api_router.exceptions import RouteNotFoundException, MethodNotAllowedException
from aiohttp import ClientSession, ClientTimeout
from app.config import config
from app.logging import logger
import json as json_module

class APIRouter:

    def __init__(self):
                
        self.config = {
            "endpoints": {                
                "/objeto": {
                    "methods": ["GET", "POST"],
                    "backend": config.OBJECT_SERVICE_URL
                },
                "/Datastreams": {
                    "methods": ["GET", "POST"],
                    "backend": config.DATASTREAMS_SERVICE_URL
                }
            },
        }

    async def route(self, request: Request):        
        service = request.path_params["path_name"].split("/")[1]
        service = "/" + service
        logger.info(f"Routing request for service: {service} with method: {request.method}")
        
        if service not in self.config["endpoints"]:
            raise RouteNotFoundException("Route not found")
        
        methods = self.config["endpoints"][service]["methods"]
        if request.method not in methods:
            raise MethodNotAllowedException(f"{request.method} not allowed")

        headers = request.headers.mutablecopy()
        headers["gateway-jwt-token"] = "Some Security Header"
        
        method = request.path_params["path_name"].split("/")[2:]
        base_url = self.config["endpoints"][service]["backend"] + service + "/" + "/".join(method)
        
        # Agregar query parameters si existen
        if request.query_params:
            query_string = str(request.query_params)
            base_url = f"{base_url}?{query_string}"
        
        logger.info(f"Forwarding to: {base_url}")
        
        timeout = ClientTimeout(total=30)

        try:
            async with ClientSession(timeout=timeout) as session:
                if request.method == "GET":
                    logger.info(f"Sending GET request")
                    async with session.get(url=base_url, headers=headers) as response:
                        data = await response.read()
                        logger.info(f"GET response: {response.status}")
                        modified_headers = dict(response.headers)
                        
                elif request.method == "POST":
                    # Leer el body una sola vez
                    body_bytes = await request.body()
                    logger.info(f"Sending POST with {len(body_bytes)} bytes")
                    
                    # Determinar Content-Type
                    content_type = request.headers.get("content-type", "")
                    
                    # Enviar la petición
                    async with session.post(
                        url=base_url, 
                        data=body_bytes,
                        headers=headers
                    ) as response:
                        data = await response.read()
                        logger.info(f"POST response: {response.status}")
                        modified_headers = dict(response.headers)
                else:
                    return Response(content="Method not supported", status_code=405)
                
                self.add_headers(modified_headers)
                return Response(content=data, status_code=response.status, headers=modified_headers)
                
        except Exception as e:
            logger.error(f"Error forwarding request: {e}")
            return Response(content=f"Error: {str(e)}", status_code=500)
                
    def add_headers(self, modified_headers):
        modified_headers['X-XSS-Protection'] = '1; mode=block'
        modified_headers['X-Frame-Options'] = 'DENY'
        modified_headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
        modified_headers['X-Content-Type-Options'] = 'nosniff'
        modified_headers['Expires'] = '0'
        modified_headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        modified_headers['Pragma'] = 'no-cache'