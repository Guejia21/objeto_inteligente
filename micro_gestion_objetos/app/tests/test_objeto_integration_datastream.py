import pytest

from app.application.objeto_service import ObjetoService
from app.domain.ObjetoInteligente import ObjetoInteligente
from app.infraestructure.IRepository import IRepository
from app.infraestructure.logging.ILogPanelMQTT import ILogPanelMQTT


# Fakes mínimos solo para log y persistencia (NO tocan Datastreams)
class FakeLogPanel(ILogPanelMQTT):
    async def Publicar(self, topic: str, message):
        return

    async def PubLog(self, *args, **kwargs):
        return

    async def PubUserLog(self, *args, **kwargs):
        return

    async def PubRawLog(self, *args, **kwargs):
        return


class FakePersistence(IRepository):
    def save_object_metadata(self, metadata: dict):
        pass

    def get_object_metadata(self) -> dict:
        return {}

    def is_object_metadata_exists(self) -> bool:
        return True


@pytest.fixture
def objeto_service_real():
    """
    Fixture de integración REAL:
    - No hace monkeypatch a dataStream_service.
    - Usa la implementación real que hace requests.get al microservicio Datastreams.
    """
    # Reset del singleton
    ObjetoInteligente._instance = None

    service = ObjetoService(FakeLogPanel(), FakePersistence())
    # El osid debe coincidir con el del metadata.json del micro de Datastreams
    service.objetoInteligente.update_attributes("ESP32_Sala", "Sensor de Temperatura Sala")
    return service


@pytest.mark.asyncio
async def test_integration_get_state_real_with_datastream(objeto_service_real: ObjetoService):
    """
    IT-OBJ-REAL-01:
    Prueba de integración REAL: ObjetoService.get_state + microservicio Datastreams.

    Requiere:
    - Microservicio Datastreams levantado.
    - metadata.json con OSID = "ESP32_Sala" y datastreams 'temperatura' y 'led'.
    """
    result = await objeto_service_real.get_state("ESP32_Sala")

    # 1) El osid debe mantenerse
    assert result["osid"] == "ESP32_Sala"

    # 2) Debe venir la lista de datastreams
    assert "datastreams" in result
    assert len(result["datastreams"]) >= 2

    # 3) Nombres normalizados que espera Gestión de Objetos
    nombres = {ds["variableEstado"] for ds in result["datastreams"]}
    assert "temperatura" in nombres
    assert "led" in nombres
