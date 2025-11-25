""""Data Transfer Objects (DTOs) para la aplicación de gestión de objetos inteligentes."""
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class Unit(BaseModel):
    symbol: str
    label: str
    unitType: int


class Datastream(BaseModel):
    datastream_format: str
    feedid: Optional[str]
    id: str
    current_value: Optional[Any]
    at: str
    max_value: str
    min_value: str
    tags: List[str]
    unit: Unit
    datapoints: Optional[Any]


class Location(BaseModel):
    name: Optional[str]
    domain: int
    lat: str
    lon: str
    ele: str
    exposure: int
    disposition: int


class Feed(BaseModel):
    id: str
    title: str
    Private: bool
    tags: List[str]
    description: str
    feed: str
    auto_feed_url: Optional[str]
    status: int
    updated: str
    created: str
    creator: str
    version: Optional[Any]
    website: Optional[Any]
    datastreams: List[Datastream]
    location: Location
    TitleHTML: str
    URLMostrar: str


class ObjectData(BaseModel):
    Conceptos: List[str]
    lugares: Optional[Any]
    feed: Feed
    pathfeed: str
    DocumentJSON: Optional[Any]
