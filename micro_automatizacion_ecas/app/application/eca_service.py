from ast import Dict
import os
import random
import time
from application.dtos import ECAResponse, MakeContractRequest
from infra.logging.Logging import logger
from config import settings
from application import ontology_service
from infra.logging.ILogPanelMQTT import ILogPanelMQTT
from domain.eca import ECA
from domain.eca_task_manager import eca_task_manager


class EcaService:
    def __init__(self, log_panel: ILogPanelMQTT):
        self.pathEca = settings.PATH_ECA        
        self.osid = ontology_service.get_id()
        self.title = ontology_service.get_title()
        self.Log = log_panel
        self.eca = ECA()        
        
    async def crear_eca(self, eca_data: MakeContractRequest) -> ECAResponse:
        """
        Crea un nuevo contrato ECA basado en los datos proporcionados.
        """
        if not self.osid:
            logger.error("No se pudo obtener el ID del objeto inteligente desde la ontología.")
            return ECAResponse(
                status="error",
                code="ONTOLOGY_ID_ERROR",
                message="No se pudo obtener el ID del objeto inteligente desde la ontología.",
                data={}
            )
        
        logger.info("Iniciando creación de ECA")
        
        if self.osid == eca_data.osid:
            try:
                # Guardar archivo del contrato
                if not os.path.exists(self.pathEca):
                    os.makedirs(self.pathEca, mode=0o777, exist_ok=True)
                    
                filename = f"ECA_{eca_data.osidDestino}_{random.random()}.json"
                filepath = os.path.join(self.pathEca, filename)
                
                with open(filepath, 'w', encoding='utf-8') as fout:
                    fout.write(eca_data.contrato.model_dump_json())
                    
            except Exception as e:
                logger.error(f"Error al guardar el archivo del contrato ECA: {e}")
                return ECAResponse(
                    status="error",
                    code="FILE_SAVE_ERROR",
                    message="Error al guardar el archivo del contrato ECA.",
                    data={}
                )
            
            try:
                # Obtener diccionario aplanado del ECA
                logger.info("Agregando ECA a la Ontología")
                diccEca = self.eca.getDiccionarioECA(filename)
                diccEca['user_eca'] = eca_data.email
                
                # Poblar ontología
                if not ontology_service.poblate_eca(diccEca):
                    logger.error("Error al poblar el ECA en la ontología.")
                    return ECAResponse(
                        status="error",
                        code="ONTOLOGY_ERROR",
                        message="Error al poblar el ECA en la ontología.",
                        data={}
                    )
                
                logger.info(f"ECA {diccEca['name_eca']} guardado en ontología")
                
                # Registrar ECA en el gestor de tareas para monitoreo
                if await eca_task_manager.register_eca(diccEca):
                    logger.info(f"ECA {diccEca['name_eca']} registrado para monitoreo")
                    return ECAResponse(
                        status="success",
                        code="ECA_CREATED",
                        message="El contrato ECA ha sido creado exitosamente.",
                        data={
                            "eca_name": diccEca["name_eca"],
                            "state": diccEca["state_eca"],
                            "filename": filename
                        }
                    )
                else:
                    logger.error("Error al registrar el ECA en el gestor de tareas.")
                    return ECAResponse(
                        status="error",
                        code="TASK_MANAGER_ERROR",
                        message="Error al registrar el ECA en el gestor de tareas.",
                        data={}
                    )            
            except Exception as e:
                logger.error(f"Error creando ECA: {e}")
                import traceback
                traceback.print_exc()
                return ECAResponse(
                    status="error",
                    code="ECA_CREATION_ERROR",
                    message=f"Error al crear el ECA: {str(e)}",
                    data={}
                )
        else:
            return ECAResponse(
                status="error",
                code="INVALID_OSID",
                message="El identificador del objeto no corresponde.",
                data={}
            )
    
    def cambiar_estado_eca(self, eca_name: str, new_state: str, user_eca: str = "default") -> ECAResponse:
        """
        Cambia el estado de un ECA (on/off)
        """
        try:
            # Actualizar en ontología
            if ontology_service.update_eca_state(eca_name, new_state, user_eca):
                # Actualizar en el gestor de tareas
                eca_task_manager.update_eca_state(eca_name, new_state, user_eca)
                
                return ECAResponse(
                    status="success",
                    code="ECA_STATE_UPDATED",
                    message=f"Estado del ECA {eca_name} actualizado a {new_state}",
                    data={"eca_name": eca_name, "state": new_state}
                )
            else:
                return ECAResponse(
                    status="error",
                    code="ECA_NOT_FOUND",
                    message=f"No se encontró el ECA {eca_name}",
                    data={}
                )
        except Exception as e:
            logger.error(f"Error cambiando estado de ECA: {e}")
            return ECAResponse(
                status="error",
                code="ECA_STATE_ERROR",
                message=str(e),
                data={}
            )
    
    def eliminar_eca(self, eca_name: str, user_eca: str = "default") -> ECAResponse:
        """
        Elimina un ECA
        """
        try:
            # Eliminar del gestor de tareas
            eca_task_manager.unregister_eca(eca_name, user_eca)
            
            # Eliminar de ontología
            if ontology_service.delete_eca(eca_name, user_eca):
                return ECAResponse(
                    status="success",
                    code="ECA_DELETED",
                    message=f"ECA {eca_name} eliminado correctamente",
                    data={"eca_name": eca_name}
                )
            else:
                return ECAResponse(
                    status="error",
                    code="ECA_NOT_FOUND",
                    message=f"No se encontró el ECA {eca_name}",
                    data={}
                )
        except Exception as e:
            logger.error(f"Error eliminando ECA: {e}")
            return ECAResponse(
                status="error",
                code="ECA_DELETE_ERROR",
                message=str(e),
                data={}
            )
    
    def obtener_ecas_activos(self) -> Dict:
        """Retorna todos los ECAs activos en monitoreo"""
        return eca_task_manager.get_active_ecas()