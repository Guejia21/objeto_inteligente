import logging

# Configuración básica del logger
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a logging.INFO o logging.ERROR en producción
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Enviar logs a la consola        
    ]
)

# Crear un logger específico para este módulo
logger = logging.getLogger(__name__)