import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.deps import get_objeto_service
from app.application.objeto_service import ObjetoService
from app.domain.ObjetoInteligente import ObjetoInteligente
from app.application.dtos import ObjectData, Feed, Datastream, Unit, Location
from app.infraestructure.IRepository import IRepository
from app.infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT
from app.application import ontology_service


# --------- Fakes internos (MQTT y persistencia) ----------

class FakeLogPanel(ILogPanelMQTT):
    async def Publicar(self, topic: str, message):
        return

    async def PubLog(
        self, key: str, id_emisor: int, nombre_emisor: str,
        id_receptor: int, nombre_receptor: str, elemento: str, estado: str
    ):
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
        return self.metadata

    def is_object_metadata_exists(self) -> bool:
        return self.metadata is not None


@pytest.fixture
def test_client(monkeypatch):
    """
    Cliente de pruebas de FastAPI con un ObjetoService compartido
    y dependencias internas fake (MQTT, persistencia).
    """
    # Resetear singleton
    ObjetoInteligente._instance = None

    # Ontología inactiva para que startObject intente poblarla
    monkeypatch.setattr(ontology_service, "is_active", lambda: False)

    # Stub realista de poblate_ontology (no toca OWL en esta prueba)
    def fake_poblate_ontology(data: dict) -> bool:
        return True

    monkeypatch.setattr(ontology_service, "poblate_ontology", fake_poblate_ontology)

    fake_log = FakeLogPanel()
    fake_persistence = FakePersistence()
    service = ObjetoService(fake_log, fake_persistence)

    # Usar SIEMPRE el mismo servicio en todos los endpoints
    def override_get_objeto_service():
        return service

    app.dependency_overrides[get_objeto_service] = override_get_objeto_service

    client = TestClient(app)
    yield client

    # Limpiar overrides al finalizar
    app.dependency_overrides.clear()


def build_objectdata_payload() -> dict:
    """Construye el JSON que espera /objeto/StartObject."""
    unit = {
        "symbol": "°C",
        "label": "Celsius",
        "unitType": 1
    }
    datastream = {
        "datastream_format": "float",
        "feedid": "ESP32_Sala",
        "id": "temperatura",
        "current_value": "22.5",
        "at": "2025-11-13T12:00:00Z",
        "max_value": "100",
        "min_value": "-40",
        "tags": ["temp"],
        "unit": unit,
        "datapoints": None
    }
    location = {
        "name": "Sala",
        "domain": 1,
        "lat": "0",
        "lon": "0",
        "ele": "0",
        "exposure": 0,
        "disposition": 0
    }
    feed = {
        "id": "ESP32_Sala",
        "title": "ESP32 Sala",
        "Private": False,
        "tags": ["esp32", "sala"],
        "description": "Feed de ejemplo",
        "feed": "esp32/sala",
        "auto_feed_url": None,
        "status": 1,
        "updated": "2025-11-13T12:00:00Z",
        "created": "2025-11-13T12:00:00Z",
        "creator": "dev",
        "version": None,
        "website": None,
        "datastreams": [datastream],
        "location": location,
        "TitleHTML": "",
        "URLMostrar": ""
    }
    return {
        "Conceptos": ["demo"],
        "lugares": None,
        "feed": feed,
        "pathfeed": "",
        "DocumentJSON": None
    }


# ====================== PRUEBA DE COMPONENTE ======================

def test_component_start_and_get_identificator_flow(test_client: TestClient):
    """
    CT-OBJ-01:
    Prueba de componente del micro de Gestión de Objetos.
    Flujo:
    1) POST /objeto/StartObject
    2) GET  /objeto/Identificator?osid=ESP32_Sala
    Verifica que el micro sea capaz de iniciar el objeto y luego
    devolver la metadata persistida usando sus capas internas.
    """
    payload = build_objectdata_payload()

    # 1) Iniciar el objeto vía API
    resp_start = test_client.post("/objeto/StartObject", json=payload)
    assert resp_start.status_code == 200
    body_start = resp_start.json()
    assert "exito" in body_start["message"].lower() or "éxito" in body_start["message"].lower()

    # 2) Consultar identificador vía API
    resp_ident = test_client.get("/objeto/Identificator", params={"osid": "ESP32_Sala"})
    assert resp_ident.status_code == 200

    body_ident = resp_ident.json()
    assert body_ident is not None
    assert "dicObj" in body_ident
    assert body_ident["dicObj"]["id"] == "ESP32_Sala"
