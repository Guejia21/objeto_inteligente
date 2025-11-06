from fastapi import APIRouter, Query, HTTPException
from ..application.services import send_data, set_datastream, list_datastreams
from ..domain.models import SendDataQuery, SetDatastreamCmd
from ..domain.exceptions import DatastreamNotFound, InvalidCommand

router = APIRouter(tags=["datastreams"])

@router.get("/SendData")
def send_data_endpoint(
    osid: str = Query(...),
    variableEstado: str = Query(...),
    tipove: str = Query(...)
):
    try:
        q = SendDataQuery(osid=osid, variableEstado=variableEstado, tipove=tipove)  # type: ignore
        return send_data(q)
    except DatastreamNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/SetDatastream")
def set_datastream_endpoint(cmd: SetDatastreamCmd):
    try:
        return set_datastream(cmd)
    except DatastreamNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidCommand as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ListDatastreams")
def list_datastreams_endpoint(osid: str):
    # Validación ligera: no filtramos por osid, solo devolvemos catálogo
    return {"osid": osid, "resources": list_datastreams()}
