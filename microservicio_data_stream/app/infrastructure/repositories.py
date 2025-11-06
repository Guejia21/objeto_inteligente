from typing import Dict, Optional
from time import time
from ..domain.exceptions import DatastreamNotFound, InvalidCommand

class DatastreamRepo:
    """
    Repositorio en memoria que simula hardware.
    En producción, reemplaza read/write por adaptadores (GPIO, MQTT, HTTP al borde).
    """
    def __init__(self):
        self._meta: Dict[str, dict] = {}
        self._cache: Dict[str, dict] = {}

        # Catálogo inicial de ejemplo
        self.register("temp_cocina", type="sen", unit="C")
        self.register("ventilador", type="act")

    def register(self, ds_id: str, *, type: str, unit: Optional[str] = None):
        self._meta[ds_id] = {"id": ds_id, "type": type, "unit": unit}
        self._cache.setdefault(ds_id, {"value": None, "ts": 0.0})

    def meta(self, ds_id: str) -> dict:
        try:
            return self._meta[ds_id]
        except KeyError:
            raise DatastreamNotFound(ds_id)

    def list(self):
        return list(self._meta.values())

    def read(self, ds_id: str) -> dict:
        m = self.meta(ds_id)
        if m["type"] == "sen":
            # valor simulado de sensor
            val = 24.7
        else:  # act
            val = self._cache[ds_id]["value"] if self._cache[ds_id]["value"] is not None else 0
        self._cache[ds_id] = {"value": val, "ts": time()}
        return self._cache[ds_id]

    def write(self, ds_id: str, command: str) -> dict:
        m = self.meta(ds_id)
        if m["type"] != "act":
            raise InvalidCommand("not an actuator")
        cmd = str(command).lower()
        if cmd in ("on", "1", "true"):
            val = 1
        elif cmd in ("off", "0", "false"):
            val = 0
        else:
            raise InvalidCommand(cmd)
        self._cache[ds_id] = {"value": val, "ts": time()}
        return self._cache[ds_id]

# Instancia única simple (puedes inyectar si prefieres)
repo = DatastreamRepo()
