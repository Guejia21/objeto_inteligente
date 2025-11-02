import sys
import os
import logging
from typing import List, Dict, Any, Optional

# Agregar paths del sistema legacy para mantener compatibilidad
sys.path.append('./Escenario/OntologiaPck/')
sys.path.append('./Escenario/Auxiliares/')

from ConsultasOOS import ConsultasOOS
from PoblarECA import PoblarECA
from EditarECA import EditarECA

from app.domain.entities.eca import ECA
from app.domain.entities.usuario import Usuario

logger = logging.getLogger(__name__)

class OntologyRepository:
    def __init__(self):
        self.consultas = ConsultasOOS()
        self.poblar_eca = PoblarECA()
        self.editar_eca = EditarECA()
    
    async def guardar_eca(self, eca: ECA) -> bool:
        """Guarda un ECA en la ontología (similar a makeContract del legacy)"""
        try:
            dicc_eca = eca.to_legacy_dict()
            self.poblar_eca.poblarECA(dicc_eca)
            logger.info(f"ECA {eca.name_eca} guardado en ontología")
            return True
        except Exception as e:
            logger.error(f"Error guardando ECA en ontología: {e}")
            return False
    
    async def obtener_eca(self, nombre_eca: str) -> Optional[ECA]:
        """Obtiene un ECA por nombre (similar a getEca del legacy)"""
        try:
            eca_data = self.consultas.getEca(nombre_eca)
            if eca_data:
                return ECA.from_legacy_dict(eca_data)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo ECA {nombre_eca}: {e}")
            return None
    
    async def listar_ecas_usuario(self, email: str) -> List[ECA]:
        """Lista ECAs de un usuario (similar a listarEcasUsuario del legacy)"""
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
        """Lista todos los ECAs (similar a listarEcas del legacy)"""
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
        """Cambia estado de un ECA (similar a SetEcaState del legacy)"""
        try:
            self.consultas.setEcaState(estado, nombre_eca)
            logger.info(f"Estado del ECA {nombre_eca} cambiado a {estado}")
            return True
        except Exception as e:
            logger.error(f"Error cambiando estado del ECA {nombre_eca}: {e}")
            return False
    
    async def desactivar_ecas_usuario(self, email: str) -> List[str]:
        """Desactiva todos los ECAs de un usuario"""
        try:
            ecas_usuario = await self.listar_ecas_usuario(email)
            ecas_desactivados = []
            
            for eca in ecas_usuario:
                if await self.cambiar_estado_eca(eca.name_eca, "off"):
                    ecas_desactivados.append(eca.name_eca)
            
            return ecas_desactivados
        except Exception as e:
            logger.error(f"Error desactivando ECAs del usuario {email}: {e}")
            return []
    
    async def eliminar_eca(self, nombre_eca: str) -> bool:
        """Elimina un ECA (similar a eliminarEca del legacy)"""
        try:
            self.consultas.eliminarEca(nombre_eca)
            logger.info(f"ECA {nombre_eca} eliminado de la ontología")
            return True
        except Exception as e:
            logger.error(f"Error eliminando ECA {nombre_eca}: {e}")
            return False
