from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IConsultasOOS(ABC):
    """
    Interfaz abstracta para las consultas y operaciones de negocio sobre la ontología.
    Implementaciones deben encapsular el backend (rdflib, triplestore, Neo4j, etc.).
    """
    @abstractmethod
    def consultarOntoActiva(self) -> bool:
        """Verifica si la ontología instanciada está activa/disponible."""        

    @abstractmethod
    def consultarId(self) -> Optional[str]:
        """Retorna el identificador del objeto (id_object)."""

    @abstractmethod
    def consultarDescription(self) -> Optional[str]:
        """Retorna la descripción del estado (State)."""

    @abstractmethod
    def consultarPrivate(self) -> Any:
        """Retorna si el feed es privado (private)."""

    @abstractmethod
    def consultarTitle(self) -> Optional[str]:
        """Retorna el título (title) del feed."""

    @abstractmethod
    def consultarFeed(self) -> Optional[str]:
        """Retorna la URL del feed (feed)."""

    @abstractmethod
    def consultarStatus(self) -> Any:
        """Retorna el estado live/frozen (status)."""

    @abstractmethod
    def consultarUpdated(self) -> Any:
        """Retorna la fecha/tiempo de última actualización (updated)."""

    @abstractmethod
    def consultarCreated(self) -> Any:
        """Retorna la fecha de creación (created)."""

    @abstractmethod
    def consultarCreator(self) -> Any:
        """Retorna el creator del feed."""

    @abstractmethod
    def consultarVersion(self) -> Any:
        """Retorna la versión (version)."""

    @abstractmethod
    def consultarWebsite(self) -> Any:
        """Retorna la URL del website relacionado."""

    @abstractmethod
    def consultarServiceState(self) -> Any:
        """Retorna el estado del servicio inteligente (service_state)."""

    @abstractmethod
    def consultarTagsDatastream(self, idDatastream: str) -> List[Any]:
        """Retorna tags para un datastream dado."""

    @abstractmethod
    def consultarUnitDatastream(self, idDatastream: str) -> Dict[str, Any]:
        """Retorna diccionario {label, symbol} de la unidad de un datastream."""

    @abstractmethod
    def consultarDatastreams(self, idDatastream: str) -> Dict[str, Any]:
        """Retorna metadatos del datastream (min/max, format, type, tags, unit)."""

    @abstractmethod
    def consultarTagsTodosDatastreams(self) -> List[Any]:
        """Retorna tags para todos los datastreams."""

    @abstractmethod
    def consultarUnitTodosDatastreams(self) -> List[Dict[str, Any]]:
        """Retorna lista de unidades (datastream_id, label, symbol)."""

    @abstractmethod
    def consultarTodosDatastreams(self) -> List[Dict[str, Any]]:
        """Retorna lista completa de datastreams con metadatos y tags."""

    @abstractmethod
    def consultarListaIdDatastreams(self) -> List[str]:
        """Retorna lista de ids de datastreams."""

    @abstractmethod
    def consultarLocation(self) -> Dict[str, Any]:
        """Retorna localización del objeto {lon, lat, name, domain, ele}."""

    @abstractmethod
    def consultarState(self) -> Dict[str, Any]:
        """Retorna el estado completo del objeto (diccionario de propiedades)."""

    @abstractmethod
    def consultarTagsObjeto(self) -> List[Any]:
        """Retorna lista de tags del objeto."""

    @abstractmethod
    def consultarDataStreamFormat(self) -> List[Dict[str, Any]]:
        """Retorna formatos y tipos de datastreams."""

    @abstractmethod
    def consultarDataStreamFormatPorId(self, datastream_id: str) -> List[Any]:
        """Retorna formato de datastream por id."""

    @abstractmethod
    def consultarServiceIntelligent(self) -> Dict[str, Any]:
        """Retorna estado y datastreams relacionados con el servicio inteligente."""

    @abstractmethod
    def consultarMetodosSend(self) -> List[Any]:
        """Retorna instancias de métodos Send (consultar instancias)."""

    @abstractmethod
    def consultarMetodosReceive(self) -> List[Any]:
        """Retorna instancias de métodos Receive."""

    @abstractmethod
    def consultarMetodosExternal(self) -> List[Any]:
        """Retorna instancias de métodos External."""

    # ---- Métodos de metadatos y utilidades ----
    @abstractmethod
    def diccionarioMetaDatosObjeto(self) -> Dict[str, Any]:
        """Retorna diccionario con metadatos del objeto y su ubicación."""

    @abstractmethod
    def listaMetaDatosDataStreams(self) -> List[Dict[str, Any]]:
        """Retorna lista de metadatos de los datastreams."""

    # ---- ECAs (Eventos-Condición-Acción) ----
    @abstractmethod
    def tieneContrato(self, osidDestino: str) -> List[Dict[str, Any]]:
        """Consulta si existe contrato (ECA) para un destino dado."""

    @abstractmethod
    def verificarContrato(self, osid: str, osidDestino: str) -> List[Dict[str, Any]]:
        """Verifica contrato entre dos objetos."""

    @abstractmethod
    def listarDinamicEstado(self, eca_state: str) -> List[Dict[str, Any]]:
        """Lista ECAs dinámicas por estado."""

    @abstractmethod
    def estadoEca(self, eca_name: str) -> List[Dict[str, Any]]:
        """Consulta estado de una ECA por nombre."""

    @abstractmethod
    def usuarioEca(self, eca_name: str) -> List[Dict[str, Any]]:
        """Consulta usuario asociado a una ECA."""

    @abstractmethod
    def listarEcasEvento(self, osid: str, eca_state: str) -> List[Dict[str, Any]]:
        """Lista ECAs que inician por evento para un objeto y estado."""

    @abstractmethod
    def listarEcasEventoSegunUsuario(self, osid: str, state_eca: str, usuario_eca: str) -> List[Dict[str, Any]]:
        """Lista ECAs por usuario y estado."""

    @abstractmethod
    def listarEcas(self) -> List[Dict[str, Any]]:
        """Lista todas las ECAs."""

    @abstractmethod
    def listarEcasUsuario(self, user_eca: str) -> List[Dict[str, Any]]:
        """Lista ECAs asociadas a un usuario."""

    @abstractmethod
    def listarNombresEcasUsuario(self, user_eca: str) -> List[Any]:
        """Lista nombres y estados de ECAs de un usuario."""

    @abstractmethod
    def getEca(self, nombreEca: str) -> Dict[str, Any]:
        """Obtiene una ECA completa por nombre."""

    @abstractmethod
    def setServiceIntelligent(self, valorNuevo: Any) -> None:
        """Actualiza la propiedad service_state del objeto."""

    @abstractmethod
    def setEcaState(self, valorNuevo: Any, nombreECA: str) -> None:
        """Actualiza el estado de una ECA."""

    @abstractmethod
    def setEcaListState(self, listaEcas: List[List[Any]]) -> None:
        """Actualiza el estado de varias ECAs (lista de [nombre, valor])."""

    @abstractmethod
    def eliminarEca(self, nombreECA: str) -> None:
        """Elimina los individuos asociados a una ECA."""

    # ---- Helpers de transformación ----
    @abstractmethod
    def pasarListaDiccionario(self, lista: List[Any], keys: List[str]) -> Dict[str, Any]:
        """Convierte una lista (resultado SPARQL) a diccionario con claves provistas."""

    @abstractmethod
    def decodificar(self, diccionario: Dict[str, Any]) -> Dict[str, Any]:
        """Decodifica valores binarios/bytes a UTF-8 cuando sea necesario."""