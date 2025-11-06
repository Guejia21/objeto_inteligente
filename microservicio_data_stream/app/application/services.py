from ..domain.models import SendDataQuery, SetDatastreamCmd, SendDataResponse, SetDatastreamResponse
from ..domain.exceptions import DatastreamNotFound, InvalidCommand
from ..config.settings import settings
from ..infrastructure.repositories import repo

def send_data(q: SendDataQuery) -> SendDataResponse:
    if q.osid != settings.OSID:
        raise DatastreamNotFound("wrong_osid")
    meta = repo.meta(q.variableEstado)
    if meta["type"] != q.tipove:
        raise DatastreamNotFound(q.variableEstado)
    out = repo.read(q.variableEstado)
    return SendDataResponse(osid=q.osid, id=q.variableEstado, type=q.tipove, value=out["value"], ts=out["ts"])

def set_datastream(cmd: SetDatastreamCmd) -> SetDatastreamResponse:
    if cmd.osid != settings.OSID:
        raise DatastreamNotFound("wrong_osid")
    out = repo.write(cmd.idDataStream, cmd.comando)
    return SetDatastreamResponse(osid=cmd.osid, idDataStream=cmd.idDataStream, newValue=out["value"], ts=out["ts"])

def list_datastreams():
    return repo.list()
