from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
        description="Gestiona preferencias, ECAs y ontologías de usuario - Compatible con sistema legacy",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir routers
    app.include_router(personalizacion_router, prefix="", tags=["Personalización"])
    
    return app

# Crear aplicación
app = create_application()

# Event handlers separados para mejor compatibilidad
@app.on_event("startup")
async def startup_event():
    logger.info("Microservicio de Personalización iniciando...")
    logger.info(f"Servidor configurado en {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f" Log level: {settings.LOG_LEVEL}")

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("Microservicio de Personalización deteniéndose...")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,  # Solo en desarrollo
        log_level=settings.LOG_LEVEL.lower()
    )