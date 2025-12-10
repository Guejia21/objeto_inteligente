"""
    @file poblacion.py
    @brief Controlador REST para operaciones de población de ontologías.
    @details
    Proporciona endpoints para:
    - Poblar metadatos del objeto inteligente en la ontología
    - Crear/editar reglas ECA (Event-Condition-Action)
    - Cargar ontologías de usuario (upload de archivos .owl)
    - Registrar interacciones usuario-objeto
    - Eliminar ontologías de usuario
    
    Routers:
    - ontologia_router (prefix=/ontology/poblacion): poblamiento de objeto/ECA
    - ontologia_usuario_router (prefix=/ontology/poblacion_usuario): gestión de perfiles
    
    @note Los endpoints de carga de ontología pueden procesarse de forma asíncrona
          (recomendado: responder 202 Accepted y procesar en background).
    
    @author  NexTech
    @version 1.0
    @date 2025-01-10
    
    @see PoblacionService Para lógica de negocio
    @see PoblacionOntologiaUsuarioService Para operaciones de usuario
    @see docs/diagrams/flow_diagrams.md Para diagramas de procesos
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from application.poblacion_service import PoblacionOntologiaUsuarioService
from application.dtos import EcaPayloadDTO, PobladorPayloadDTO, RegistroInteraccionDTO
from deps import get_poblacion_pu_service, get_poblacion_service
from application.poblacion_service import PoblacionService

ontologia_router = APIRouter(prefix="/ontology/poblacion", tags=["Poblacion de Base de conocimiento"])
"""@var ontologia_router Router para operaciones de población del objeto inteligente."""
@ontologia_router.post("/poblar_metadatos_objeto", response_model=None,status_code=201)
async def poblar_metadatos_objeto(metadata: PobladorPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """
        @brief Puebla los metadatos del objeto inteligente en la ontología.
        
        @param metadata DTO PobladorPayloadDTO con diccionarios de objeto y recursos.
        @param service Instancia del servicio de población (inyectada).
        
        @return Status 201 Created si exitoso, o error 500 si falla.
        
        @exception ValueError Si los datos del DTO son inválidos.
        @exception RuntimeError Si falla la población de ontología.
        
        @details
        Operación que puebla la ontología OWL con:
        1. Metadatos del objeto inteligente (individuos, propiedades)
        2. Múltiples recursos asociados (datastreams, propiedades, etc.)
        
        Flujo:
        1. Extrae diccionarios del DTO
        2. Convierte a JSON para serialización
        3. Delega en servicio de población
        4. Retorna 201 Created
        
        @note Esta es una operación compuesta que requiere idempotencia:
              si se ejecuta dos veces con los mismos datos, debe ser segura
              (crear sólo si no existe, o actualizar).
        
        @see PoblacionService.poblar_metadatos_objeto()
        @see docs/diagrams/flow_diagrams.md (A) Poblar metadatos sequence
    """    
    try:
        listaRecursos = [r.model_dump() for r in metadata.dicRec]
        return service.poblar_metadatos_objeto(metadata.dicObj.model_dump(), listaRecursos)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
@ontologia_router.post("/poblar_eca", response_model=None,status_code=201)
async def poblar_eca(eca: EcaPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """
        @brief Puebla una nueva regla ECA (Event-Condition-Action) en la ontología.
        
        @param eca DTO EcaPayloadDTO con definición de la regla.
        @param service Servicio de población.
        
        @return Status 201 Created si exitoso, o error 500.
        
        @exception ValueError Si los datos de ECA son inválidos.
        @exception RuntimeError Si falla la población en ontología.
        
        @details
        Crea una nueva regla ECA en la ontología. Las ECAs son reglas
        event-driven que permiten automatizar comportamientos del objeto.
        
        @note Si la regla requiere re-reasoning costoso, considerar
              procesar de forma asíncrona (responder 202).
        
        @see PoblacionService.poblar_eca()
        @see docs/diagrams/flow_diagrams.md (C) Poblar/Editar ECA sequence
    """
    try:
        return service.poblar_eca(eca.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
@ontologia_router.post("/editar_eca", response_model=None,status_code=200)
async def editar_eca(eca: EcaPayloadDTO, service: PoblacionService = Depends(get_poblacion_service)):
    """
        @brief Edita una regla ECA existente en la ontología.
        
        @param eca DTO EcaPayloadDTO con definición actualizada de la regla.
        @param service Servicio de población.
        
        @return Status 200 OK si exitoso, o error 500.
        
        @exception ValueError Si los datos de ECA son inválidos.
        @exception RuntimeError Si falla la edición en ontología.
        
        @details
        Actualiza una regla ECA existente. Similar a poblar_eca pero
        modifica una regla previamente creada.
        
        @note Considerar sincronización: si múltiples clientes editan
              la misma ECA, puede haber condiciones de carrera.
        
        @see PoblacionService.editar_eca()
        @see docs/diagrams/flow_diagrams.md (C) Poblar/Editar ECA sequence
    """
    try:
        return service.editar_eca(eca.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

ontologia_usuario_router = APIRouter(prefix="/ontology/poblacion_usuario", tags=["Poblacion de Perfil de Usuario"])
"""@var ontologia_usuario_router Router para operaciones de ontología de usuario."""

@ontologia_usuario_router.post("/cargar_ontologia", response_model=None,status_code=201)
async def cargar_ontologia(
    file: UploadFile = File(..., description="Archivo de ontología (.owl)"),
    nombre: str = Form(..., description="Nombre de la ontología"),
    ipCoordinador: str = Form(..., description="IP del coordinador"),    
    service: PoblacionOntologiaUsuarioService = Depends(get_poblacion_pu_service)
):
    """
        @brief Carga una ontología de usuario desde archivo (.owl).
        
        @param file Archivo .owl a cargar (multipart/form-data).
        @param nombre Identificador/nombre de la ontología.
        @param ipCoordinador IP del coordinador (para notificación/registro).
        @param service Servicio de población de usuario (inyectado).
        
        @return Status 201 Created si exitoso, o error 500 si falla.
        
        @exception FileNotFoundError Si el archivo no puede procesarse.
        @exception RuntimeError Si falla la carga en el motor de ontología.
        
        @details
        Carga un archivo OWL de perfil de usuario en el sistema.
        
        Flujo:
        1. Lee contenido del archivo desde request
        2. Delega en servicio para parsear e indexar
        3. Registra en coordinador (opcional)
        
        @note Esta es una operación potencialmente larga. Considerar:
              1. Responder 202 Accepted inmediatamente
              2. Procesar el archivo en background (Job Queue)
              3. Exponer endpoint de status del job
        
        @see PoblacionOntologiaUsuarioService.cargarOntologia()
        @see docs/diagrams/flow_diagrams.md (B) Cargar ontología sequence
        
        @warning No implementar validación de tamaño de archivo podría
                 causar ataques DoS. Añadir límite MAX_FILE_SIZE.
    """
    try:
        file_content = await file.read()
        return service.cargarOntologia(file_content, nombre, ipCoordinador)        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@ontologia_usuario_router.post("/registro_interaccion", response_model=None,status_code=200)
async def registro_interaccion(
    data: RegistroInteraccionDTO,
    service: PoblacionOntologiaUsuarioService = Depends(get_poblacion_pu_service)
):
    """
        @brief Registra una interacción del usuario con un objeto inteligente.
        
        @param data DTO RegistroInteraccionDTO con detalles de la interacción.
        @param service Servicio de población de usuario.
        
        @return Status 200 OK si exitoso, o error 500.
        
        @exception ValueError Si los datos de interacción son inválidos.
        @exception RuntimeError Si falla la persistencia de la interacción.
        
        @details
        Registra eventos/interacciones del usuario con objetos en su ontología
        de perfil. Esto permite crear un historial y personalización basada
        en patrones de uso.
        
        @see PoblacionOntologiaUsuarioService.registroInteraccionUsuarioObjeto()
    """
    try:
        return service.registroInteraccionUsuarioObjeto(data)        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
@ontologia_usuario_router.delete("/eliminar_ontologia_usuario", response_model=None,status_code=200)
async def eliminar_ontologia_usuario(
    service: PoblacionOntologiaUsuarioService = Depends(get_poblacion_pu_service)
):
    """
        @brief Elimina la ontología del perfil de usuario.
        
        @param service Servicio de población de usuario.
        
        @return Status 200 OK si exitoso, o error 500.
        
        @exception RuntimeError Si falla la eliminación.
        
        @details
        Borra completamente la ontología del perfil de usuario del sistema.
        Operación destructiva.
        
        @note Considerar implementar soft-delete + job de limpieza asíncrona
              para recuperabilidad. O requerir confirmación.
        
        @see PoblacionOntologiaUsuarioService.eliminarOntologia()
        @see docs/diagrams/flow_diagrams.md (D) Eliminación sequence
    """
    try:
        return service.eliminarOntologia()        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))