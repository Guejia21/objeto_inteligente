import sys
import os
import logging
from typing import List, Optional

# Agregar paths del sistema legacy para mantener compatibilidad
sys.path.append('./Escenario/OntologiaPck/')
sys.path.append('./Escenario/Auxiliares/')

try:
    from ConsultasOOS import ConsultasOOS
    from PoblarECA import PoblarECA
    from EditarECA import EditarECA
    HAS_LEGACY_DEPS = True
except ImportError as e:
    logging.warning(f"Dependencias legacy no disponibles: {e}")
    HAS_LEGACY_DEPS = False

from app.domain.entities.eca import ECA
from app.domain.repositories.personalizacion_repository import PersonalizacionRepository

logger = logging.getLogger(__name__)

class PersonalizacionRepositoryImpl(PersonalizacionRepository):
    """Implementación concreta del repositorio usando el sistema legacy"""
    
    def __init__(self):
        if HAS_LEGACY_DEPS:
            self.consultas = ConsultasOOS()
            self.poblar_eca = PoblarECA()
            self.editar_eca = EditarECA()
        else:
            logger.warning("Usando repositorio mock - Dependencias legacy no disponibles")
            self.consultas = None
            self.poblar_eca = None
            self.editar_eca = None
    
    async def guardar_eca(self, eca: ECA) -> bool:
        """Guarda un ECA en la ontología"""
        if not HAS_LEGACY_DEPS:
            logger.warning("Mock: ECA guardado (dependencias legacy no disponibles)")
            return True
            
        try:
            dicc_eca = eca.to_legacy_dict()
            self.poblar_eca.poblarECA(dicc_eca)
            logger.info(f"ECA {eca.name_eca} guardado en ontología")
            return True
        except Exception as e:
            logger.error(f"Error guardando ECA en ontología: {e}")
            return False
    
    async def obtener_eca(self, nombre_eca: str) -> Optional[ECA]:
        """Obtiene un ECA por nombre"""
        if not HAS_LEGACY_DEPS:
            logger.warning("Mock: Retornando ECA mock")
            # Retornar un ECA mock para pruebas
            from app.domain.entities.evento_eca import EventoECA
            from app.domain.entities.accion_eca import AccionECA
            
            evento = EventoECA(
                objEvento="mock_osid",
                id_event_resource="mock_recurso_evento",
                name_event_resource="Mock Recurso Evento",
                name_event_object="Mock Objeto Evento",
                signCondicion="Condición mock",
                unidadCondicion="unidad",
                variableCondicion="100",
                comparadorCondicion="mayor"
            )
            
            accion = AccionECA(
                objAccion="mock_osid_destino",
                id_action_resource="mock_recurso_accion",
                name_action_resource="Mock Recurso Acción",
                name_action_object="Mock Objeto Acción",
                signAccion="Acción mock",
                unidadAccion="unidad",
                variableAccion="1",
                comparadorAccion="igual"
            )
            
            return ECA(
                name_eca=nombre_eca,
                eca_state="on",
                eventoECA=evento,
                accionECA=accion,
                user_eca="mock_user"
            )
        
        try:
            eca_data = self.consultas.getEca(nombre_eca)
            if eca_data:
                return ECA.from_legacy_dict(eca_data)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo ECA {nombre_eca}: {e}")
            return None
    
    async def listar_ecas_usuario(self, email: str) -> List[ECA]:
        """Lista ECAs de un usuario"""
        if not HAS_LEGACY_DEPS:
            logger.warning("Mock: Retornando lista vacía de ECAs")
            return []
        
        try:
            ecas_data = self.consultas.listarEcasUsuario(email)
            ecas = []
            for eca_data in ecas_data:
                ecas.append(ECA.from_legacy_dict(eca_data))
            return ecas
        except Exception as e:
            logger.error(f"Error listando ECAs del usuario {email}: {e}")
            return []
    
    async def listar_todos_ecas(self) -> List[ECA]:
        """Lista todos los ECAs"""
        if not HAS_LEGACY_DEPS:
            logger.warning("Mock: Retornando lista vacía de ECAs")
            return []
        
        try:
            ecas_data = self.consultas.listarEcas()
            ecas = []
            for eca_data in ecas_data:
                ecas.append(ECA.from_legacy_dict(eca_data))
            return ecas
        except Exception as e:
            logger.error(f"Error listando todos los ECAs: {e}")
            return []
    
    async def cambiar_estado_eca(self, nombre_eca: str, estado: str) -> bool:
        """Cambia estado de un ECA"""
        if not HAS_LEGACY_DEPS:
            logger.warning(f"Mock: Estado del ECA {nombre_eca} cambiado a {estado}")
            return True
        
        try:
            self.consultas.setEcaState(estado, nombre_eca)
            logger.info(f"Estado del ECA {nombre_eca} cambiado a {estado}")
            return True
        except Exception as e:
            logger.error(f"Error cambiando estado del ECA {nombre_eca}: {e}")
            return False
    
    async def desactivar_ecas_usuario(self, email: str) -> List[str]:
        """Desactiva todos los ECAs de un usuario"""
        ecas_desactivados = []
        
        try:
            ecas_usuario = await self.listar_ecas_usuario(email)
            
            for eca in ecas_usuario:
                if await self.cambiar_estado_eca(eca.name_eca, "off"):
                    ecas_desactivados.append(eca.name_eca)
            
            return ecas_desactivados
        except Exception as e:
            logger.error(f"Error desactivando ECAs del usuario {email}: {e}")
            return []
    
    async def eliminar_eca(self, nombre_eca: str) -> bool:
        """Elimina un ECA"""
        if not HAS_LEGACY_DEPS:
            logger.warning(f"Mock: ECA {nombre_eca} eliminado")
            return True
        
        try:
            self.consultas.eliminarEca(nombre_eca)
            logger.info(f"ECA {nombre_eca} eliminado de la ontología")
            return True
        except Exception as e:
            logger.error(f"Error eliminando ECA {nombre_eca}: {e}")
            return False
    
    async def verificar_usuario(self, email: str) -> bool:
        """Verifica si un usuario existe (mock por ahora)"""
        # Por ahora siempre retorna True para pruebas
        # En producción, conectar con sistema de autenticación legacy
        return True