from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse  #  ESTE IMPORT
from infrastructure.logging.Logging import logger
import uvicorn

from application.controllers.personalizacion_controller import router as personalizacion_router
from config.settings import settings

def create_application() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    
    app = FastAPI(
        title="Microservicio de Personalización",
        description="Gestiona preferencias e interacciones de usuario - Compatible con sistema legacy",        
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir routers
    app.include_router(personalizacion_router)
    
    return app

# Crear aplicación
app = create_application()

# Exception handlers globales -
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Error interno del servidor: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    logger.warning(f"🔍 Recurso no encontrado: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"detail": "Recurso no encontrado"}
    )
@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url='/docs')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=settings.PORT)