""""Data Transfer Objects (DTOs) para la aplicación de gestión de objetos inteligentes."""
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class Unit(BaseModel):
    symbol: str = Field(..., description="Símbolo de la unidad (e.g., '°C', 'm/s')", json_schema_extra={"example": "°C"})
    label: str = Field(..., description="Etiqueta de la unidad", json_schema_extra={"example": "Grados Celsius"})
    unitType: int = Field(..., description="Tipo de unidad", json_schema_extra={"example": 1})


class Datastream(BaseModel):
    datastream_format: str = Field(..., description="Formato del datastream (e.g., 'float', 'bool')", json_schema_extra={"example": "float"})
    feedid: Optional[str] = Field(None, description="Identificador del feed asociado", json_schema_extra={"example": "feed123"})
    id: str = Field(..., description="Identificador del datastream", json_schema_extra={"example": "datastream123"})
    current_value: Optional[Any] = Field(None, description="Valor actual del datastream", json_schema_extra={"example": 23.5})
    at: str = Field(..., description="Fecha y hora del valor actual", json_schema_extra={"example": "2024-04-27T12:00:00Z"})
    max_value: str = Field(..., description="Valor máximo registrado", json_schema_extra={"example": "100"})
    min_value: str = Field(..., description="Valor mínimo registrado", json_schema_extra={"example": "0"})
    tags: List[str] = Field(..., description="Lista de etiquetas asociadas al datastream", json_schema_extra={"example": ["temperatura", "sensor"]})
    unit: Unit
    datapoints: Optional[Any]

class DatastreamEstadoItem(BaseModel):
    variableEstado: str = Field(..., description="Identificador del datastream")
    type: str = Field(..., description="Tipo de dato (float, bool, etc.)")
    valor: Any = Field(..., description="Valor actual del datastream")
    dstype: str = Field(..., description="Tipo de datastream (sensor/actuador)")


class Location(BaseModel):
    name: Optional[str] = Field(None, description="Nombre de la ubicación", json_schema_extra={"example": "Oficina Principal"})
    domain: int = Field(..., description="Dominio de la ubicación", json_schema_extra={"example": 1})
    lat: str = Field(..., description="Latitud de la ubicación", json_schema_extra={"example": "40.7128"})
    lon: str = Field(..., description="Longitud de la ubicación", json_schema_extra={"example": "-74.0060"})
    ele: str = Field(..., description="Elevación de la ubicación", json_schema_extra={"example": "10"})
    exposure: int = Field(..., description="Exposición de la ubicación", json_schema_extra={"example": 2})
    disposition: int = Field(..., description="Disposición de la ubicación")


class Feed(BaseModel):
    id: str = Field(..., description="Identificador del objeto", json_schema_extra={"example": "objeto123"})
    title: str = Field(..., description="Título del objeto inteligente", json_schema_extra={"example": "Mi Objeto Inteligente"})
    Private: bool = Field(..., description="Indica si el feed es privado", json_schema_extra={"example": False})
    tags: List[str] = Field(..., description="Lista de etiquetas asociadas al objeto", json_schema_extra={"example": ["etiqueta1", "etiqueta2"]})
    description: str = Field(..., description="Descripción del objeto inteligente", json_schema_extra={"example": "Este es un objeto inteligente para monitoreo ambiental"})
    feed: str = Field(..., description="Identificador del feed", json_schema_extra={"example": "feed123"})
    auto_feed_url: Optional[str] = Field(None, description="URL automática del feed", json_schema_extra={"example": "http://example.com/feed"})
    status: int = Field(..., description="Estado del objeto inteligente", json_schema_extra={"example": 1})
    updated: str = Field(..., description="Fecha de última actualización", json_schema_extra={"example": "2024-04-27T12:00:00Z"})
    created: str = Field(..., description="Fecha de creación", json_schema_extra={"example": "2024-01-01T12:00:00Z"})
    creator: str = Field(..., description="Creador del objeto inteligente", json_schema_extra={"example": "admin"})
    version: Optional[Any] = Field(None, description="Versión del objeto inteligente", json_schema_extra={"example": "1.0"})
    website: Optional[Any] = Field(None, description="Sitio web asociado", json_schema_extra={"example": "http://example.com"})
    datastreams: List[Datastream]
    location: Location
    TitleHTML: str
    URLMostrar: str


class ObjectData(BaseModel):
    Conceptos: List[str] = Field(..., description="Lista de conceptos asociados al objeto inteligente",json_schema_extra={"example": ["sala de estar", "oficina"]})
    lugares: Optional[Any] = Field(None, description="Información de lugares asociados", json_schema_extra={"example": "edificio"})
    feed: Feed
    pathfeed: str = Field(..., description="Ruta del feed asociado", json_schema_extra={"example": "/path/to/feed"})
    DocumentJSON: Optional[Any]
