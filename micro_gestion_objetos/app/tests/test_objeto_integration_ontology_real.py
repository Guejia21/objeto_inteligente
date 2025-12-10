import pytest

from app.application.objeto_service import ObjetoService
from app.domain.ObjetoInteligente import ObjetoInteligente
from app.application.dtos import ObjectData, Feed, Datastream, Unit, Location
from app.infraestructure.IRepository import IRepository
from app.infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT
from app.application import ontology_service




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
        self._metadata = None

    def save_object_metadata(self, metadata: dict):
        self._metadata = metadata

    def get_object_metadata(self) -> dict:
        return self._metadata

    def is_object_metadata_exists(self) -> bool:
        return self._metadata is not None


@pytest.fixture
def fake_feed():
    """Feed de ejemplo compatible con tu DTO."""
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
        datapoints=None,
    )
    loc = Location(
        name="Sala",
        domain=1,
        lat="0",
        lon="0",
        ele="0",
        exposure=0,
        disposition=0,
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
        URLMostrar="",
    )
    return feed


@pytest.fixture
def objeto_service_real_ontology(monkeypatch):
    """
    ObjetoService que:
    - Usa persistence y log falsos
    - NO mockea poblate_ontology (llama al micro de ontología real)
    - Solo fuerza is_active = False para que sí intente poblar.
    """
    # Resetear singleton
    ObjetoInteligente._instance = None

    # Forzamos que la ontología NO esté activa para que startObject llame a poblate_ontology
    monkeypatch.setattr(ontology_service, "is_active", lambda: False)

    service = ObjetoService(FakeLogPanel(), FakePersistence())
    return service


@pytest.mark.asyncio
async def test_integration_start_object_real_with_ontology(
    objeto_service_real_ontology: ObjetoService,
    fake_feed: Feed,
):
    """
    IT-OBJ-ONT-REAL-01:
    Prueba de integración REAL entre micro de Gestión de Objeto y micro de Ontología.

    Flujo:
    ObjetoService.startObject -> ontology_service.poblate_ontology (HTTP POST)
    -> FastAPI /ontology/poblacion/poblar_metadatos_objeto -> PoblacionService
    -> PobladorOOS -> OWL.

    Requisitos:
    - Micro de Ontología ejecutándose en config.urlOntologyService (p.ej. http://localhost:8001/ontology)
    - Ontología base accesible (config.ontologia)
    """
    data = ObjectData(
        Conceptos=["demo"],
        lugares=None,
        feed=fake_feed,
        pathfeed="",
        DocumentJSON=None,
    )

    # Llamamos al método real, que hará el POST al micro de ontología
    result = await objeto_service_real_ontology.startObject(data)

    # 1) Debe indicar éxito
    msg = result["message"].lower()
    assert "exito" in msg or "éxito" in msg

    # 2) Debe haber guardado metadata en persistence
    assert objeto_service_real_ontology.persistence.is_object_metadata_exists()

    # 3) El objeto inteligente debe quedar inicializado con el osid del feed
    assert objeto_service_real_ontology.objetoInteligente.osid == "ESP32_Sala"
