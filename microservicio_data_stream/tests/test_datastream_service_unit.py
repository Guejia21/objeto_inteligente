# tests/test_datastream_service_unit.py

from services.datastream_service import DatastreamService
from config import Config


class FakeExecutor:
    """Simula el módulo que obtiene valores de datastreams."""
    def __init__(self, value):
        self.value = value
        self.last_datastream = None
        self.get_value_calls = 0  # para contar cuántas veces se llamó get_value

    def get_value(self, datastream_id):
        self.last_datastream = datastream_id
        self.get_value_calls += 1
        return self.value


class FakeResponse:
    """Simula ResponseHelper para no depender de su implementación real."""
    def __init__(self):
        self.last_call = None

    def simple_value(self, osid, variable_estado, datastream_format, value):
        self.last_call = ("simple_value", osid, variable_estado, datastream_format, value)
        # estructura simplificada para los asserts
        return {
            "kind": "simple_value",
            "osid": osid,
            "datastream_id": variable_estado,
            "format": datastream_format,
            "value": value,
        }

    def error(self, message, code, details=None):
        self.last_call = ("error", message, code, details)
        return {
            "kind": "error",
            "message": message,
            "code": code,
            "details": details,
        }


def _make_service_for_tests():
    """Crea un DatastreamService aislado de archivos y hardware."""
    service = DatastreamService()

    # Simulamos metadata en memoria
    service.datastreams = [
        {
            "datastream_id": "temp",
            "datastream_format": "int",
            "datastream_type": "sensor",
        }
    ]

    # Inyectamos los mocks
    service.executor = FakeExecutor(value=25)
    service.response = FakeResponse()

    # OSID esperado
    Config.OSID = "ESP32_LED_01"

    return service

def test_send_data_ok():
    """Caso feliz: OSID correcto, tipo=1 y datastream existente."""
    service = _make_service_for_tests()

    result = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="temp",
        tipove="1",
    )

    assert result["kind"] == "simple_value"
    assert result["osid"] == "ESP32_LED_01"
    assert result["datastream_id"] == "temp"
    assert result["value"] == 25
    assert service.executor.last_datastream == "temp"


def test_send_data_osid_incorrecto():
    """Debe devolver error cuando el OSID no coincide."""
    service = _make_service_for_tests()

    result = service.send_data(
        osid="OTRO_OSID",
        variable_estado="temp",
        tipove="1",
    )

    assert result["kind"] == "error"
    assert result["code"] == Config.CODES["idIncorrecto"]


def test_send_data_tipo_no_implementado():
    """Debe devolver error cuando tipove != 1."""
    service = _make_service_for_tests()

    result = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="temp",
        tipove="2",  # tipo inválido
    )

    assert result["kind"] == "error"
    assert result["code"] == Config.CODES["noImplementado"]


def test_send_data_datastream_no_existe():
    """Debe devolver error cuando el datastream no existe en metadata."""
    service = _make_service_for_tests()
    # dejamos datastreams vacío para forzar el error
    service.datastreams = []

    result = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="no_existe",
        tipove="1",
    )

    assert result["kind"] == "error"
    assert result["code"] == Config.CODES["dataStremNoExiste"]

def test_datastream_exists_true_and_false():
    """Prueba unitaria de datastream_exists para casos verdadero y falso."""
    service = _make_service_for_tests()

    assert service.datastream_exists("temp") is True
    assert service.datastream_exists("otro") is False


def test_get_datastream_info_returns_metadata():
    """Prueba unitaria de get_datastream_info."""
    service = _make_service_for_tests()

    info = service.get_datastream_info("temp")
    assert info is not None
    assert info["datastream_id"] == "temp"
    assert info["datastream_format"] == "int"
    assert info["datastream_type"] == "sensor"


def test_send_data_default_format_string():
    """
    Si en la metadata no viene 'datastream_format',
    el servicio asume 'string' por defecto (según implementación real).
    """
    service = _make_service_for_tests()
    service.datastreams = [
        {
            "datastream_id": "temp",
            # sin 'datastream_format'
            "datastream_type": "sensor",
        }
    ]

    result = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="temp",
        tipove="1",
    )

    assert result["format"] == "string"



def test_send_data_respects_datastream_format():
    """
    Si en la metadata el 'datastream_format' es 'float',
    debe propagarse en la respuesta.
    """
    service = _make_service_for_tests()
    service.datastreams = [
        {
            "datastream_id": "temp",
            "datastream_format": "float",
            "datastream_type": "sensor",
        }
    ]

    result = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="temp",
        tipove="1",
    )

    assert result["format"] == "float"


def test_send_data_calls_executor_once():
    """Verifica que get_value se llama exactamente una vez por petición."""
    service = _make_service_for_tests()

    _ = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="temp",
        tipove="1",
    )

    assert service.executor.get_value_calls == 1


def test_send_data_response_structure():
    """Verifica que la respuesta tenga la estructura mínima esperada."""
    service = _make_service_for_tests()

    result = service.send_data(
        osid="ESP32_LED_01",
        variable_estado="temp",
        tipove="1",
    )

    for key in ("kind", "osid", "datastream_id", "format", "value"):
        assert key in result
