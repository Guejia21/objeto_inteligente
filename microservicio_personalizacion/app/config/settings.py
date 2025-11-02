import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Configuración FastAPI
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8001"))
    
    # Configuración RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
    
    # Configuración paths legacy (mantener compatibilidad)
    ONTOLOGY_PATH = os.getenv("ONTOLOGY_PATH", "./ontologies")
    SERVICIOWEB_URL = os.getenv("SERVICIOWEB_URL", "http://localhost:8080")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()