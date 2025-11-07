from fastapi import Request, Response
from app.api_router.exceptions import RouteNotFoundException, MethodNotAllowedException
from aiohttp import ClientSession
from app.config import config
from app.logging import logger
class APIRouter:

    def __init__(self):
                
        self.config = {
            "endpoints": {
                "/ontology": {
                    "methods": ["GET", "POST"],
                    "backend": config.ONTOLOGY_SERVICE_URL
                },
                "/objeto": {
                    "methods": ["GET", "POST"],
                    "backend": config.OBJECT_SERVICE_URL
                }
            },
        }

    async def route(self, request: Request):        
        #La ruta solicitada se muestra en formato /servicio/recurso, así que se debe extraer el primer segmento
        service = request.path_params["path_name"].split("/")[1]
        service = "/" + service  # Reconstruir el path con el formato esperado
        # TODO: Log the critical parameters: Client IP, Timestamp etc. for monitoring and analytics
        print(f"Routing request for service: {service} with method: {request.method}")
        # If a random path is accessed, don't forward to backend
        if service not in self.config["endpoints"]:
            # TODO: Log for audit
            raise RouteNotFoundException("Route not found")
        
        # If incorrect method for the path is accessed, don't forward to backend
        methods = self.config["endpoints"][service]["methods"]
        if request.method not in methods:
            # TODO: Log for audit
            raise MethodNotAllowedException(f"{request.method} not allowed")

        # TODO: Add any additional request validation here

        # Add API headers to the request so that backend can ensure the request is coming from APIGateway
        headers = request.headers.mutablecopy()

        # Send a JWT token from API Header here which backend can validate
        headers["gateway-jwt-token"] = "Some Security Header"
        method = request.path_params["path_name"].split("/")[2:]  # Extract the method part of the path
        # Route the request
        base_url = self.config["endpoints"][service]["backend"] + service + "/" + "/".join(method)

        async with ClientSession() as session:

            match request.method:
                # TODO: Pass all of the parameters and body
                case "GET":
                    try:
                        response = await session.get(url=base_url, headers=headers)
                    except Exception as e:
                        logger.error(f"Error occurred while forwarding GET request: {e}")
                        return Response(content="Error forwarding request", status_code=500)
                case "POST":
                    try:
                        # Leer el body del request
                        body = await request.body()
                        
                        # Determinar si es JSON o form data
                        content_type = request.headers.get("content-type", "")
                        
                        if "application/json" in content_type:
                            # Si es JSON, parsear y enviar como json
                            json_data = await request.json()
                            response = await session.post(url=base_url, json=json_data, headers=headers)
                        else:
                            # Si no es JSON, enviar como data raw
                            response = await session.post(url=base_url, data=body, headers=headers)
                            
                    except Exception as e:
                        logger.error(f"Error occurred while forwarding POST request: {e}")
                        return Response(content="Error forwarding request", status_code=500)
                # TODO: Other methods
                
            data = await response.content.read()
            modified_headers = response.headers.copy()
            self.add_headers(modified_headers)
            return Response(content=data, status_code=response.status, headers=modified_headers)
                
    def add_headers(self, modified_headers):
        # OWASP Secure Headers https://owasp.org/www-project-secure-headers/
        modified_headers['X-XSS-Protection'] = '1; mode=block'
        modified_headers['X-Frame-Options'] = 'DENY'
        modified_headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
        modified_headers['X-Content-Type-Options'] = 'nosniff'

        # Avoid Caching Tokens
        modified_headers['Expires'] = '0'
        modified_headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        modified_headers['Pragma'] = 'no-cache'