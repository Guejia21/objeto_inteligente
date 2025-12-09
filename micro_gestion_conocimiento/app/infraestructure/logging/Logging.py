"""Logger de consola para la aplicación."""
import logging

# Configuración básica del logger
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a logging.INFO o logging.ERROR en producción
    format="%(levelname)s       %(asctime)s  %(message)s",
    handlers=[
        logging.StreamHandler(),  # Enviar logs a la consola        
    ]
)
logging.getLogger("multipart").setLevel(logging.WARNING)
logging.getLogger("multipart.multipart").setLevel(logging.WARNING)
logging.getLogger("python_multipart").setLevel(logging.WARNING)

# Crear un logger específico para este módulo
logger = logging.getLogger(__name__)