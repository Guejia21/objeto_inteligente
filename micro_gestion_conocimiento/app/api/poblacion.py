
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from application.poblacion_service import PoblacionOntologiaUsuarioService
from application.dtos import EcaPayloadDTO, PobladorPayloadDTO
from deps import get_poblacion_service
from application.poblacion_service import PoblacionService

ontologia_router = APIRouter(prefix="/ontology/poblacion", tags=["Poblacion de Base de conocimiento"])
@ontologia_router.post("/poblar_metadatos_objeto", response_model=None,status_code=201)
async def poblar_metadatos_objeto(metadata: PobladorPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """Endpoint para poblar los metadatos del objeto inteligente."""    
    try:
        listaRecursos = [r.model_dump() for r in metadata.dicRec]
        return service.poblar_metadatos_objeto(metadata.dicObj.model_dump(), listaRecursos)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
@ontologia_router.post("/poblar_eca", response_model=None,status_code=201)
async def poblar_eca(eca: EcaPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """Endpoint para poblar una regla ECA en la base de conocimiento."""
    try:
        return service.poblar_eca(eca.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
@ontologia_router.post("/editar_eca", response_model=None,status_code=200)
async def editar_eca(eca: EcaPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """Endpoint para editar una regla ECA en la base de conocimiento."""
    try:
        return service.editar_eca(eca.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

ontologia_usuario_router = APIRouter(prefix="/ontology/poblacion_usuario", tags=["Poblacion de Perfil de Usuario"])
@ontologia_usuario_router.post("/cargar_ontologia", response_model=None,status_code=201)
async def cargar_ontologia(
    file: UploadFile = File(..., description="Archivo de ontología (.owl)"),
    nombre: str = Form(..., description="Nombre de la ontología"),
    ipCoordinador: str = Form(..., description="IP del coordinador"),    
):
    """Endpoint para cargar la ontología del perfil de usuario."""
    try:
        file_content = await file.read()
        PoblacionOntologiaUsuarioService().cargar_ontologia(file_content, nombre, ipCoordinador)
        return {"status": "Carga exitosa"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))