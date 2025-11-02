import logging
import json
from typing import Dict, Any, List, Optional

from app.domain.entities.usuario import Usuario
from app.domain.entities.preferencia import Preferencia
from app.domain.entities.eca import ECA, EventoECA, AccionECA
from app.domain.repositories.personalizacion_repository import PersonalizacionRepository  

logger = logging.getLogger(__name__)

class PersonalizacionService:
    def __init__(self, repository: PersonalizacionRepository):  #Usa la interfaz
        self.repository = repository

    
    async def crear_preferencia(self, preferencia: Preferencia) -> Dict[str, Any]:
        """Crea una preferencia/ECA (similar a makeContract del legacy)"""
        try:
            # 1. Verificar usuario (similar a ModuloDePersonalizacion.verificarUsuario)
            usuario = Usuario(email=preferencia.email, osid=preferencia.osid)
            if not await self._verificar_usuario(usuario):
                return {"error": "usuario no esta", "status_code": 401}
            
            # 2. Validar contrato (similar a validaciones del legacy)
            if not preferencia.validar_contrato():
                return {"error": "Parámetro faltante/contrato inválido", "status_code": 400}
            
            # 3. Verificar duplicados (similar a verificaciones del legacy)
            if await self._existe_eca_duplicado(preferencia):
                return {"error": "preferencia ya existe", "status_code": 409}
            
            # 4. Convertir preferencia a ECA
            eca = await self._convertir_preferencia_a_eca(preferencia)
            
            # 5. Guardar en ontología (similar a poblarEca)
            if not await self.repository.guardar_eca(eca):
                return {"error": "Error interno del servidor", "status_code": 500}
            
            # 6. Publicar evento (si está configurado)
            await self._publicar_evento_preferencia_creada(preferencia, eca)
            
            return {"mensaje": "Contrato creado correctamente", "status_code": 200}
            
        except Exception as e:
            logger.error(f"Error creando preferencia: {e}")
            return {"error": "Error interno del servidor", "status_code": 500}
    
    async def listar_ecas_usuario(self, email: str, osid: str) -> Dict[str, Any]:
        """Lista ECAs de un usuario"""
        try:
            ecas = await self.repository.listar_ecas_usuario(email)
            
            # Convertir a formato legacy compatible
            ecas_legacy = []
            for eca in ecas:
                ecas_legacy.append(eca.to_legacy_dict())
            
            return {
                "ecas": ecas_legacy,
                "status_code": 200
            }
        except Exception as e:
            logger.error(f"Error listando ECAs del usuario {email}: {e}")
            return {"error": "Error al listar ECAs", "status_code": 500}
    
    async def desactivar_ecas_usuario(self, email: str, osid: str) -> Dict[str, Any]:
        """Desactiva todos los ECAs de un usuario (similar a NotificarSalidaDeUsuario)"""
        try:
            ecas_desactivados = await self.repository.desactivar_ecas_usuario(email)
            
            return {
                "mensaje": f"{len(ecas_desactivados)} ECAs desactivados",
                "ecas_desactivados": ecas_desactivados,
                "status_code": 200
            }
        except Exception as e:
            logger.error(f"Error desactivando ECAs del usuario {email}: {e}")
            return {"error": "Error al desactivar ECAs", "status_code": 500}
    
    async def cambiar_estado_eca(self, osid: str, nombre_eca: str, estado: str) -> Dict[str, Any]:
        """Cambia estado de un ECA (similar a SetEcaState del legacy)"""
        try:
            if estado not in ["on", "off"]:
                return {"error": "estado inválido", "status_code": 400}
            
            if await self.repository.cambiar_estado_eca(nombre_eca, estado):
                return {"mensaje": f"ECA {nombre_eca} {estado}", "status_code": 200}
            else:
                return {"error": "Error cambiando estado del ECA", "status_code": 500}
                
        except Exception as e:
            logger.error(f"Error cambiando estado del ECA {nombre_eca}: {e}")
            return {"error": "Error interno del servidor", "status_code": 500}
    
    async def eliminar_eca(self, osid: str, nombre_eca: str) -> Dict[str, Any]:
        """Elimina un ECA (similar a eliminarEca del legacy)"""
        try:
            if await self.repository.eliminar_eca(nombre_eca):
                return {"mensaje": f"ECA {nombre_eca} eliminado", "status_code": 200}
            else:
                return {"error": "Error eliminando ECA", "status_code": 500}
        except Exception as e:
            logger.error(f"Error eliminando ECA {nombre_eca}: {e}")
            return {"error": "Error interno del servidor", "status_code": 500}
    
    # Métodos privados
    async def _verificar_usuario(self, usuario: Usuario) -> bool:
        """Verifica si el usuario está autenticado (similar al legacy)"""
        # Por ahora simulamos la verificación
        # En producción, conectar con el módulo de autenticación legacy
        return usuario.verificar_autenticacion()
    
    async def _existe_eca_duplicado(self, preferencia: Preferencia) -> bool:
        """Verifica si ya existe un ECA similar (similar a verificaciones del legacy)"""
        # Lógica de verificación de duplicados
        ecas_usuario = await self.repository.listar_ecas_usuario(preferencia.email)
        
        # Comparar con los ECAs existentes
        for eca in ecas_usuario:
            if (eca.eventoECA.objEvento == preferencia.osid and 
                eca.accionECA.objAccion == preferencia.osidDestino):
                return True
        return False
    
    async def _convertir_preferencia_a_eca(self, preferencia: Preferencia) -> ECA:
        """Convierte una preferencia a ECA (similar a getDiccionarioECA del legacy)"""
        contrato = preferencia.contrato
        
        # Crear evento ECA
        evento = EventoECA(
            objEvento=preferencia.osid,
            id_event_resource=contrato['evento']['recurso'],
            name_event_resource=contrato['evento'].get('nombre_recurso', ''),
            name_event_object=contrato['evento'].get('nombre_objeto', ''),
            signCondicion=contrato['evento'].get('descripcion', ''),
            unidadCondicion=contrato['evento'].get('unidad', ''),
            variableCondicion=str(contrato['evento']['valor']),
            comparadorCondicion=contrato['evento']['operador']
        )
        
        # Crear acción ECA
        accion = AccionECA(
            objAccion=preferencia.osidDestino,
            id_action_resource=contrato['accion']['recurso'],
            name_action_resource=contrato['accion'].get('nombre_recurso', ''),
            name_action_object=contrato['accion'].get('nombre_objeto', ''),
            signAccion=contrato['accion'].get('descripcion', ''),
            unidadAccion=contrato['accion'].get('unidad', ''),
            variableAccion=str(contrato['accion']['valor']),
            comparadorAccion=contrato['accion'].get('operador', 'igual')
        )
        
        # Crear ECA
        nombre_eca = f"eca_{preferencia.email}_{preferencia.osid}_{len(await self.repository.listar_ecas_usuario(preferencia.email)) + 1}"
        
        return ECA(
            name_eca=nombre_eca,
            eca_state="on",  # Por defecto activado como en legacy
            eventoECA=evento,
            accionECA=accion,
            user_eca=preferencia.email
        )
    
    async def _publicar_evento_preferencia_creada(self, preferencia: Preferencia, eca: ECA):
        """Publica evento de preferencia creada (si está configurado)"""
        # Por ahora es un placeholder para futura integración con message broker
        pass
