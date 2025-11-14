import os

MICRO_GESTION_KNOWLEDGE_URL = os.getenv(
    "MICRO_GESTION_KNOWLEDGE_URL",
    "http://localhost:8000"  # ajusta host/puerto según tu docker-compose
)

# Timeout por defecto para llamadas HTTP
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10.0"))
