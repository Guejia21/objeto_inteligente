"""
    @file main.py
    @brief Punto de entrada y configuración de la aplicación FastAPI para micro_gestion_objetos.
    @details
    Define la aplicación FastAPI, registra routers, y configura el servidor ASGI.
    Este microservicio gestiona el ciclo de vida de objetos inteligentes:
    creación, consultas de estado, envío de datos, y comunicación con datastreams.
    
    @author  NexTech
    @version 1.0.0
    @date 2025-01-10
    
    @see objeto_controller Para endpoints REST
    @see ObjetoService Para lógica de negocio
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.objeto_controller import router
from config import settings

app = FastAPI(
    title="Microservicio de Gestión de Objetos Inteligentes",
    version="1.0.0",
    description="Gestiona el ciclo de vida de objetos inteligentes: creación, estado, datastreams",
    docs_url="/docs",
    redoc_url="/redoc"
)
"""@var app Instancia de FastAPI para micro_gestion_objetos."""

app.include_router(router)

@app.get('/', include_in_schema=False)
def redirect_to_docs():
    """
        @brief Redirige raíz a documentación Swagger.
        
        @return RedirectResponse a /docs.
    """
    return RedirectResponse(url='/docs')

if __name__ == '__main__':
    """
        @brief Punto de entrada para ejecución local/desarrollo.
        
        @details
        Inicia el servidor ASGI uvicorn con configuración de settings.
        En producción, usar: `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`
    """
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=settings.PORT)