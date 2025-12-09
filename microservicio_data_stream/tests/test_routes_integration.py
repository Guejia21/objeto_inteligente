# tests/test_routes_integration.py
# Prueba de integración: DatastreamService + ResponseHelper reales
# con metadata inyectada y un executor fake.

import json

from services.datastream_service import DatastreamService
from config import Config


class FakeExecutor:
    """Executor falso que simula devolver siempre el mismo valor."""
    def __init__(self, value):
        self.value = value
        self.last_datastream = None

    def get_value(self, datastream_id):
        self.last_datastream = datastream_id
        return self.value


def test_send_data_integration_real_flow():
    """
    Prueba de integración:
    - Usa DatastreamService REAL (ResponseHelper real).
    - Inyecta metadata de datastreams en memoria.
    - Inyecta un executor falso (simula hardware).
    - Ejecuta send_data y valida la respuesta.
    """
    service = DatastreamService()

    # Inyectamos metadata manualmente (en vez de depender de metadata.json)
    service.datastreams = [
        {
            "datastream_id": "temp",
            "datastream_format": "int",
            "datastream_type": "sensor",
        }
    ]

    # Inyectamos un executor que simula un valor de 99
    fake_exec = FakeExecutor(value=99)
    service.executor = fake_exec

    # OSID correcto
    Config.OSID = "ESP32_LED_01"

    # Ejecutamos el flujo real de send_data
    result = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="temp",
        tipove="1",
    )

    # La respuesta puede ser JSON (str) o dict, según tu ResponseHelper
    if isinstance(result, str):
        data = json.loads(result)
    elif isinstance(result, bytes):
        data = json.loads(result.decode())
    elif isinstance(result, dict):
        data = result
    else:
        raise AssertionError(f"Tipo de respuesta no esperado: {type(result)}")

    # Validaciones mínimas de integración según la estructura REAL:
    # {'osid', 'datastream', 'datatype', 'value', 'timestamp'}

    # 1) OSID correcto
    assert data.get("osid") == "ESP32_LED_01"

    # 2) Datastream correcto
    assert data.get("datastream") == "temp"

    # 3) Tipo de dato coherente
    assert data.get("datatype") == "int"

    # 4) Valor devuelto por el servicio (debe venir del FakeExecutor)
    assert data.get("value") == 99

    # 5) Se generó un timestamp (no validamos formato, solo que exista)
    assert "timestamp" in data

    # 6) El executor fue llamado con el datastream correcto
    assert fake_exec.last_datastream == "temp"