from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ObjectMetadata(BaseModel):
    id: str = Field(..., description="Identificador del objeto")
    ip_object: Optional[str] = None
    version: Optional[str] = None
    creator: Optional[str] = None
    status: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    private: Optional[bool] = None
    description: Optional[str] = None
    updated: Optional[str] = None
    website: Optional[str] = None
    feed: Optional[str] = None
    created: Optional[str] = None

    # Campos usados por poblarLocation (en tu código pasan el mismo diccionario)
    name: Optional[str] = None
    domain: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    ele: Optional[float] = None

    @field_validator("tags", mode="before")
    def ensure_tags_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)


class DataStream(BaseModel):
    datastream_id: str = Field(..., description="ID del datastream (usado como IRI base)")
    datastream_format: Optional[str] = None
    feedid: Optional[Any] = None
    current_value: Optional[Any] = None
    at: Optional[str] = None
    max_value: Optional[Any] = None
    min_value: Optional[Any] = None
    tags: List[str] = Field(default_factory=list)
    datapoints: Optional[Any] = None
    symbol: Optional[str] = None
    label: Optional[str] = None
    unitType: Optional[int] = None
    datastream_type: Optional[str] = None
    featureofinterest: Optional[str] = None
    entityofinterest: Optional[str] = None

    @field_validator("tags", mode="before")
    def ensure_ds_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)


class PobladorPayloadDTO(BaseModel):
    # se ajustó a los nombres de variables que usas en el código
    dicObj: ObjectMetadata = Field(..., description="Diccionario con metadatos del objeto")
    dicRec: List[DataStream] = Field(..., description="Lista de datastreams (recursos)")

    @field_validator("dicRec", mode="before")
    def ensure_list_dicrec(cls, v):
        if v is None:
            return []
        return list(v)