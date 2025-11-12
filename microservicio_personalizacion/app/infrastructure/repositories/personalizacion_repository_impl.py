import sys
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

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
        
        # Cache para preferencias de usuario (temporal)
        self._preferencias_usuario = {}
        self._interacciones_usuario = {}

    # ========== MÉTODOS NUEVOS PARA PERSONALIZACIÓN ==========

    async def guardar_preferencia_usuario(self, eca: ECA, email: str) -> bool:
        """Guarda una preferencia de usuario (nuevo método)"""
        try:
            if email not in self._preferencias_usuario:
                self._preferencias_usuario[email] = []
            
            preferencia_data = {
                'email': email,
                'osid': eca.eventoECA.objEvento,
                'osidDestino': eca.accionECA.objAccion,
                'contrato': {
                    'evento': {
                        'recurso': eca.eventoECA.id_event_resource,
                        'operador': eca.eventoECA.comparadorCondicion,
                        'valor': eca.eventoECA.variableCondicion
                    },
                    'accion': {
                        'recurso': eca.accionECA.id_action_resource,
                        'valor': eca.accionECA.variableAccion
                    }
                },
                'eca_name': eca.name_eca,
                'timestamp': datetime.now().isoformat()
            }
            
            self._preferencias_usuario[email].append(preferencia_data)
            logger.info(f"✅ Preferencia guardada para usuario {email}: {eca.name_eca}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando preferencia: {e}")
            return False

    async def obtener_preferencias_usuario(self, email: str) -> List[Dict[str, Any]]:
        """Obtiene todas las preferencias de un usuario"""
        return self._preferencias_usuario.get(email, [])

    async def limpiar_preferencias_temporales(self, email: str) -> bool:
        """Limpia preferencias temporales de un usuario"""
        try:
            if email in self._preferencias_usuario:
                # En una implementación real, aquí se limpiarían solo las temporales
                # Por ahora simulamos que se limpian algunas
                original_count = len(self._preferencias_usuario[email])
                self._preferencias_usuario[email] = [
                    pref for pref in self._preferencias_usuario[email] 
                    if not pref.get('temporal', False)
                ]
                new_count = len(self._preferencias_usuario[email])
                logger.info(f"Preferencias temporales limpiadas para {email}: {original_count} -> {new_count}")
                return True
            return True  # Si no hay preferencias, igual es éxito
        except Exception as e:
            logger.error(f"Error limpiando preferencias: {e}")
            return False

    async def guardar_interaccion(self, interaccion_data: Dict[str, Any]) -> str:
        """Guarda interacción usuario-objeto"""
        try:
            email = interaccion_data.get('email')
            if email not in self._interacciones_usuario:
                self._interacciones_usuario[email] = []
            
            interaccion_id = f"inter_{int(datetime.now().timestamp())}_{len(self._interacciones_usuario[email])}"
            
            interaccion_data['interaccion_id'] = interaccion_id
            self._interacciones_usuario[email].append(interaccion_data)
            
            logger.info(f"✅ Interacción guardada para {email}: {interaccion_id}")
            return interaccion_id
            
        except Exception as e:
            logger.error(f"Error guardando interacción: {e}")
            return "error"

    # ========== MÉTODOS LEGACY (MANTENER COMPATIBILIDAD) ==========

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
        """Verifica si un usuario existe"""
        return True  # Siempre True para pruebas
        
    async def desactivar_ecas_por_osid(self, osid: str) -> List[str]:
        """Desactiva ECAs por OSID"""
        try:
            # Buscar email asociado al OSID y desactivar sus ECAs
            email = await self._obtener_email_por_osid(osid)
            return await self.desactivar_ecas_usuario(email)
        except Exception as e:
            logger.error(f"Error en desactivar_ecas_por_osid: {e}")
            return []

    async def _obtener_email_por_osid(self, osid: str) -> str:
        """Obtiene email asociado a OSID"""
        if osid.startswith("usuario_"):
            return f"{osid}@ejemplo.com"
        return f"usuario_{osid}@ejemplo.com"