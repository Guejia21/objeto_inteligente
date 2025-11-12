from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  #  ESTE IMPORT
import logging
import uvicorn

from app.application.controllers.personalizacion_controller import router as personalizacion_router
from app.config.settings import settings

# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('microservicio_personalizacion.log')
    ]
)

logger = logging.getLogger(__name__)

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

     # Middleware para logging de requests
    @app.middleware("http")
    async def log_requests(request, call_next):
        logger.info(f" {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f" {request.method} {request.url} - Status: {response.status_code}")
        return response
    
    # Incluir routers
    app.include_router(personalizacion_router, prefix="", tags=["Personalización"])
    
    return app

# Crear aplicación
app = create_application()

# Event handlers separados para mejor compatibilidad
@app.on_event("startup")
async def startup_event():
    logger.info("Microservicio de Personalización v2.0 iniciando...")
    logger.info(f"Servidor configurado en {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f" Log level: {settings.LOG_LEVEL}")
    logger.info(" Responsabilidades: Preferencias de usuario e interacciones")
    logger.info(" Microservicios coordinados: Ontologías, Automatización")

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("Microservicio de Personalización deteniéndose...")

# Exception handlers globales -
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"💥 Error interno del servidor: {exc}")
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

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )