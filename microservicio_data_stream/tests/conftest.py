# tests/conftest.py
import sys
from pathlib import Path

# Ruta a la carpeta del proyecto: .../microservicio_data_stream
ROOT_DIR = Path(__file__).resolve().parents[1]

# Ruta a app/infrastructure/adapters (donde están services, routes, lib, utils...)
ADAPTERS_DIR = ROOT_DIR / "app" / "infrastructure" / "adapters"

for p in [ROOT_DIR, ADAPTERS_DIR]:
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
