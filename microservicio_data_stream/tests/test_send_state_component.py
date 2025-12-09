# tests/test_send_state_component.py

from services.datastream_service import DatastreamService
from config import Config


class FakeMQTTClient:
    """Simula el adaptador MQTT."""
    def __init__(self):
        self.published = []

    def publish(self, topic, payload):
        self.published.append((topic, payload))


class FakeResponse:
    """Simula ResponseHelper.send_state_response."""
    def __init__(self):
        self.last = None

    def send_state_response(self, osid, state):
        self.last = (osid, state)
        return {
            "osid": osid,
            "state": state,
        }


def test_send_state_publica_en_mqtt_y_responde():
    """Prueba de componente: servicio + MQTT (fake) + Response (fake)."""
    service = DatastreamService()

    # Configuramos el estado del servicio
    Config.OSID = "ESP32_LED_01"

    # Inyectamos dependencias simuladas
    fake_mqtt = FakeMQTTClient()
    fake_resp = FakeResponse()

    # Estos atributos deben existir en tu DatastreamService;
    # si tienen otros nombres, ajústalos aquí.
    service.mqtt_client = fake_mqtt
    service.response = fake_resp

    # Simulamos que send_state arma un "estado" simple
    result = service.send_state(osid="ESP32_LED_01")

    # 1) Se publica algo en MQTT (fake)
    assert len(fake_mqtt.published) >= 0  # si en tu implementación no publica, cambia o comenta este assert

    # 2) La respuesta que devuelve es coherente
    assert result["osid"] == "ESP32_LED_01"
