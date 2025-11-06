from pydantic import BaseModel, Field
from typing import Optional, Literal, Any

DatastreamType = Literal["sen", "act"]

class Datastream(BaseModel):
    id: str
    type: DatastreamType
    unit: Optional[str] = None

class SendDataQuery(BaseModel):
    osid: str
    variableEstado: str
    tipove: DatastreamType

class SetDatastreamCmd(BaseModel):
    osid: str
    idDataStream: str
    comando: str
    email: Optional[str] = None
    mac: Optional[str] = None
    dateInteraction: Optional[str] = None

class SendDataResponse(BaseModel):
    osid: str
    id: str
    type: DatastreamType
    value: Any
    ts: float = Field(..., description="Epoch seconds")

class SetDatastreamResponse(BaseModel):
    status: str = "OK"
    osid: str
    idDataStream: str
    newValue: Any
    ts: float = Field(..., description="Epoch seconds")
