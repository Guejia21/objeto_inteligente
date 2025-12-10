# conftest.py en la RAÍZ de micro_automatizacion_ecas
import sys
from pathlib import Path

# Carpeta raíz del proyecto (donde está app/, tests/, etc.)
ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "app"

# Añadimos ROOT_DIR para poder hacer "import app"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Añadimos APP_DIR para que funcionen imports como:
# "from infra..." , "from domain..." , "from application..."
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Debug opcional
print(">>> conftest ROOT cargado. ROOT_DIR =", ROOT_DIR)
print(">>> APP_DIR =", APP_DIR)
print(">>> sys.path[0:4] =", sys.path[0:4])
