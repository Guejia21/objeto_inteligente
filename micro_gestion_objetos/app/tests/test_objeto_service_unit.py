# tests/test_objeto_service_unit.py

import pytest
from unittest.mock import MagicMock
import asyncio

from app.application.objeto_service import ObjetoService
from app.domain.ObjetoInteligente import ObjetoInteligente
from app.application.dtos import ObjectData, Feed, Datastream, Unit, Location
from app.infraestructure.IRepository import IRepository
from app.infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT

# Módulos que vamos a “monkeypatchear”
from app.application import ontology_service, dataStream_service


# ---------- Fakes / Mocks básicos ----------

class FakeLogPanel(ILogPanelMQTT):
    async def Publicar(self, topic: str, message):
        return

    async def PubLog(self, key: str, id_emisor: int, nombre_emisor: str,
                     id_receptor: int, nombre_receptor: str, elemento: str, estado: str):
        return

    async def PubUserLog(self, entidad_interes: str, objeto: str, recurso: str, estado: str):
        return

    async def PubRawLog(self, objeto: str, recurso: str, value: str):
        return


class FakePersistence(IRepository):
    def __init__(self):
        self.metadata = None

    def save_object_metadata(self, metadata: dict):
        self.metadata = metadata

    def get_object_metadata(self) -> dict:
        if self.metadata is None:
            raise FileNotFoundError("No hay metadata guardada")
        return self.metadata

    def is_object_metadata_exists(self) -> bool:
        return self.metadata is not None


@pytest.fixture
def fake_feed():
    """Feed mínimo válido para pruebas de startObject."""
    unit = Unit(symbol="°C", label="Celsius", unitType=1)
    ds = Datastream(
        datastream_format="float",
        feedid="ESP32_Sala",
        id="temperatura",
        current_value="22.5",
        at="2025-11-13T12:00:00Z",
        max_value="100",
        min_value="-40",
        tags=["temp"],
        unit=unit,
        datapoints=None
    )
    loc = Location(
        name="Sala",
        domain=1,
        lat="0",
        lon="0",
        ele="0",
        exposure=0,
        disposition=0
    )
    feed = Feed(
        id="ESP32_Sala",
        title="ESP32 Sala",
        Private=False,
        tags=["esp32", "sala"],
        description="Feed de ejemplo",
        feed="esp32/sala",
        auto_feed_url=None,
        status=1,
        updated="2025-11-13T12:00:00Z",
        created="2025-11-13T12:00:00Z",
        creator="dev",
        version=None,
        website=None,
        datastreams=[ds],
        location=loc,
        TitleHTML="",
        URLMostrar=""
    )
    return feed


@pytest.fixture
def objeto_service(monkeypatch, fake_feed):
    """
    Crea un ObjetoService con:
    - ontology_service simulado
    - dataStream_service simulado
    - persistence fake
    - log_panel fake
    """
    # Resetear singleton entre pruebas
    ObjetoInteligente._instance = None

    # ontología inactiva por defecto para el __init__
    monkeypatch.setattr(ontology_service, "is_active", lambda: False)

    fake_persistence = FakePersistence()
    fake_log = FakeLogPanel()
    service = ObjetoService(fake_log, fake_persistence)

    # Ahora simulamos ontología activa cuando se necesite
    def fake_is_active():
        return True

    def fake_get_id():
        return "ESP32_Sala"

    def fake_get_title():
        return "ESP32 Sala"

    def fake_poblate_ontology(data: dict) -> bool:
        # Simular que poblar ontología siempre funciona
        return True

    monkeypatch.setattr(ontology_service, "is_active", fake_is_active)
    monkeypatch.setattr(ontology_service, "get_id", fake_get_id)
    monkeypatch.setattr(ontology_service, "get_title", fake_get_title)
    monkeypatch.setattr(ontology_service, "poblate_ontology", fake_poblate_ontology)

    # Simular dataStream_service
    def fake_send_state(osid: str):
        return {
            "osid": osid,
            "timestamp": "2025-11-13T12:00:00Z",
            "datastreams": [
                {
                    "datastream_id": "temperatura",
                    "datastream_format": "float",
                    "current_value": "25.0",
                    "datastream_type": "sensor",
                }
            ],
        }

    def fake_send_service_state() -> bool:
        return True

    def fake_send_data(osid: str, variable_estado: str, tipove: str = "1"):
        return {"osid": osid, "variableEstado": variable_estado, "valor": "30.0"}

    monkeypatch.setattr(dataStream_service, "send_state", fake_send_state)
    monkeypatch.setattr(dataStream_service, "send_service_state", fake_send_service_state)
    monkeypatch.setattr(dataStream_service, "send_data", fake_send_data)

    # Iniciar objeto en ontología para tener osid cargado
    service.objetoInteligente.update_attributes("ESP32_Sala", "ESP32 Sala")

    return service

@pytest.mark.asyncio 
async def test_get_identificator_ok(objeto_service: ObjetoService): 
    """UT1: getIdentificator devuelve metadata si el osid coincide y hay metadata.""" 
    # Preparar metadata en persistence 
    objeto_service.persistence.save_object_metadata({"dicObj": {"id": "ESP32_Sala"}}) 
    result = await objeto_service.getIdentificator("ESP32_Sala") 
   
    assert result is not None 
    assert result["dicObj"]["id"] == "ESP32_Sala"


@pytest.mark.asyncio
async def test_get_identificator_osid_mismatch(objeto_service: ObjetoService):
    """UT2: getIdentificator devuelve mensaje si el osid no coincide."""
    result = await objeto_service.getIdentificator("OTRO_OBJETO")
    assert isinstance(result, dict)
    assert "no coincide" in result["message"]


@pytest.mark.asyncio
async def test_start_object_when_inactive_ok(objeto_service: ObjetoService, fake_feed, monkeypatch):
    """UT3: startObject inicia el objeto cuando la ontología está inactiva y datos son válidos."""
    # Asegurar que la ontología esté INACTIVA en esta prueba
    monkeypatch.setattr(ontology_service, "is_active", lambda: False)

    # Dejar el objeto sin osid (opcional, pero está bien)
    objeto_service.objetoInteligente.update_attributes(None, None)

    data = ObjectData(
        Conceptos=["demo"],
        lugares=None,
        feed=fake_feed,
        pathfeed="",
        DocumentJSON=None
    )

    result = await objeto_service.startObject(data)

    # Debe devolver mensaje de éxito
    assert "exito" in result["message"].lower() or "éxito" in result["message"].lower()
    # Y debe haber guardado metadata
    assert objeto_service.persistence.is_object_metadata_exists()

@pytest.mark.asyncio
async def test_start_object_when_already_active(objeto_service: ObjetoService, fake_feed, monkeypatch):
    """UT4: startObject devuelve mensaje si la ontología ya está activa."""
    # is_active ya está simulado como True en el fixture
    data = ObjectData(
        Conceptos=["demo"],
        lugares=None,
        feed=fake_feed,
        pathfeed="",
        DocumentJSON=None
    )

    result = await objeto_service.startObject(data)
    assert "ya está activo" in result["message"]


@pytest.mark.asyncio
async def test_get_state_ok_normalization(objeto_service: ObjetoService):
    """UT5: get_state normaliza correctamente datastreams desde dataStream_service."""
    result = await objeto_service.get_state("ESP32_Sala")
    assert result["osid"] == "ESP32_Sala"
    assert "datastreams" in result
    assert len(result["datastreams"]) == 1
    ds = result["datastreams"][0]
    assert ds["variableEstado"] == "temperatura"
    assert ds["type"] == "float"
    assert ds["valor"] == "25.0"


@pytest.mark.asyncio
async def test_get_state_osid_mismatch(objeto_service: ObjetoService):
    """UT6: get_state lanza ValueError cuando el osid no coincide."""
    with pytest.raises(ValueError):
        await objeto_service.get_state("OTRO_OBJETO")


@pytest.mark.asyncio
async def test_send_service_state_ok(objeto_service: ObjetoService):
    """UT7: send_service_state retorna service_available True cuando datastream está ok."""
    result = await objeto_service.send_service_state()
    assert result["service_available"] is True


@pytest.mark.asyncio
async def test_send_data_ok(objeto_service: ObjetoService):
    """UT8: send_data retorna el resultado del dataStream_service correctamente."""
    result = await objeto_service.send_data("ESP32_Sala", "temperatura", "1")
    assert result["osid"] == "ESP32_Sala"
    assert result["variableEstado"] == "temperatura"
    assert result["valor"] == "30.0"


@pytest.mark.asyncio
async def test_send_data_osid_mismatch(objeto_service: ObjetoService):
    """UT9: send_data lanza ValueError cuando el osid no coincide."""
    with pytest.raises(ValueError):
        await objeto_service.send_data("OTRO_OBJETO", "temperatura", "1")


@pytest.mark.asyncio
async def test_send_data_missing_variable_estado(objeto_service: ObjetoService):
    """UT10: send_data lanza ValueError cuando variableEstado está vacío."""
    with pytest.raises(ValueError):
        await objeto_service.send_data("ESP32_Sala", "", "1")
