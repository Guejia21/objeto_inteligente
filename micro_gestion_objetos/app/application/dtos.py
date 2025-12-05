""""Data Transfer Objects (DTOs) para la aplicación de gestión de objetos inteligentes."""
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class Unit(BaseModel):
    symbol: str = Field(..., description="Símbolo de la unidad (e.g., '°C', 'm/s')", json_schema_extra={"example": "°C"})
    label: str = Field(..., description="Etiqueta de la unidad", json_schema_extra={"example": "Centigrados"})
    unitType: int = Field(..., description="Tipo de unidad", json_schema_extra={"example": 0})


class Datastream(BaseModel):
    datastream_format: str = Field(..., description="Formato del datastream (e.g., 'float', 'bool')", json_schema_extra={"example": "float"})
    feedid: Optional[str] = Field(None, description="Identificador del feed asociado", json_schema_extra={"example": None})
    id: str = Field(..., description="Identificador del datastream", json_schema_extra={"example": "temperatura"})
    current_value: Optional[Any] = Field(None, description="Valor actual del datastream", json_schema_extra={"example": None})
    at: str = Field(..., description="Fecha y hora del valor actual", json_schema_extra={"example": "12/03/2020 20:38:32"})
    max_value: str = Field(..., description="Valor máximo registrado", json_schema_extra={"example": "4095.0"})
    min_value: str = Field(..., description="Valor mínimo registrado", json_schema_extra={"example": "-192.0"})
    tags: List[str] = Field(..., description="Lista de etiquetas asociadas al datastream", json_schema_extra={"example": ["Caracteristica Temperatura", "Entidad Sala", "Sensor"]})
    unit: Unit
    datapoints: Optional[Any]

class DatastreamEstadoItem(BaseModel):
    variableEstado: str = Field(..., description="Identificador del datastream")
    type: str = Field(..., description="Tipo de dato (float, bool, etc.)")
    valor: Any = Field(..., description="Valor actual del datastream")
    dstype: str = Field(..., description="Tipo de datastream (sensor/actuador)")


class Location(BaseModel):
    name: Optional[str] = Field(None, description="Nombre de la ubicación", json_schema_extra={"example": None})
    domain: int = Field(..., description="Dominio de la ubicación", json_schema_extra={"example": 0})
    lat: str = Field(..., description="Latitud de la ubicación", json_schema_extra={"example": "2.4471309"})
    lon: str = Field(..., description="Longitud de la ubicación", json_schema_extra={"example": "-76.5981505"})
    ele: str = Field(..., description="Elevación de la ubicación", json_schema_extra={"example": "4"})
    exposure: int = Field(..., description="Exposición de la ubicación", json_schema_extra={"example": 0})
    disposition: int = Field(..., description="Disposición de la ubicación", json_schema_extra={"example": 0})


class Feed(BaseModel):
    id: str = Field(..., description="Identificador del objeto", json_schema_extra={"example": "708637323"})
    title: str = Field(..., description="Título del objeto inteligente", json_schema_extra={"example": "Regulador de Temperatura"})
    Private: bool = Field(..., description="Indica si el feed es privado", json_schema_extra={"example": False})
    tags: List[str] = Field(..., description="Lista de etiquetas asociadas al objeto", json_schema_extra={"example": ["Entidad Sala", "Entity Living Room", "Temperature Regulator"]})
    description: str = Field(..., description="Descripción del objeto inteligente", json_schema_extra={"example": "Es un servicio que permite mantener la temperatura deseada por el usuario en el entorno de la sala de estar. Cuenta con un sensor de temperatura, un calefactor para incrementarla y un ventilador para decrementarla."})
    feed: str = Field(..., description="Identificador del feed", json_schema_extra={"example": "https://api.xively.com/v2/feeds/708637323.json"})
    auto_feed_url: Optional[str] = Field(None, description="URL automática del feed", json_schema_extra={"example": None})
    status: int = Field(..., description="Estado del objeto inteligente", json_schema_extra={"example": 0})
    updated: str = Field(..., description="Fecha de última actualización", json_schema_extra={"example": "12/03/2020 20:38:32"})
    created: str = Field(..., description="Fecha de creación", json_schema_extra={"example": "07/07/2015 22:03:46"})
    creator: str = Field(..., description="Creador del objeto inteligente", json_schema_extra={"example": "https://personal.xively.com/users/manzamb"})
    version: Optional[Any] = Field(None, description="Versión del objeto inteligente", json_schema_extra={"example": None})
    website: Optional[Any] = Field(None, description="Sitio web asociado", json_schema_extra={"example": None})
    datastreams: List[Datastream]
    location: Location
    TitleHTML: str = Field(..., json_schema_extra={"example": "<a style=\"color: #336600; font-size:110%;\"  href=\"https://xively.com/feeds/708637323\" >Regulador de Temperatura</a>"})
    URLMostrar: str = Field(..., json_schema_extra={"example": "https://xively.com/feeds/708637323"})


class ObjectData(BaseModel):
    Conceptos: List[str] = Field(..., description="Lista de conceptos asociados al objeto inteligente", json_schema_extra={"example": ["sala de estar"]})
    lugares: Optional[Any] = Field(None, description="Información de lugares asociados", json_schema_extra={"example": None})
    feed: Feed
    pathfeed: str = Field(..., description="Ruta del feed asociado", json_schema_extra={"example": "D:\\Aplicaciones\\SemanticSearchIoT\\WSSemanticSearch\\App_Data\\Json_Data\\708637323.json"})
    DocumentJSON: Optional[Any] = Field(None, json_schema_extra={"example": None})