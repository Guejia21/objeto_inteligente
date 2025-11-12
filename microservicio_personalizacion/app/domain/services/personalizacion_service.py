import email
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile
import os
import httpx  


from app.domain.entities.usuario import Usuario
from app.domain.entities.preferencia import Preferencia
from app.domain.entities.eca import ECA, EventoECA, AccionECA
from app.domain.repositories.personalizacion_repository import PersonalizacionRepository
from app.config.settings import settings

logger = logging.getLogger(__name__)

class PersonalizacionService:
    def __init__(self, repository: PersonalizacionRepository):
        self.repository = repository
        # Ya NO manejamos ontologías localmente
        # Toda la gestión de ontologías va al microservicio especializado

    async def crear_preferencia(self, preferencia_request) -> Dict[str, Any]:
        """Crea una preferencia/ECA - SOLO lógica de personalización"""
        try:
            # 1. Verificar usuario
            if not await self._verificar_usuario(preferencia_request.email):
                return {"error": "usuario no esta", "status_code": 401}
            
            # 2. Validar contrato básico
            if not self._validar_contrato_basico(preferencia_request.contrato):
                return {"error": "Parámetro faltante/contrato inválido", "status_code": 400}
            
            # 3. Verificar duplicados
            if await self._existe_preferencia_duplicada(preferencia_request):
                return {"error": "preferencia ya existe", "status_code": 409}
            
            # 4. CONSULTAR ONTOLOGÍA para validar recursos
            validacion_ontologia = await self._validar_recursos_con_ontologia(
                preferencia_request.contrato, 
                preferencia_request.osid, 
                preferencia_request.osidDestino
            )
            
            if not validacion_ontologia.get("valido", False):
                return {
                    "error": f"Recursos no válidos en ontología: {validacion_ontologia.get('error', 'Error desconocido')}",
                    "status_code": 400
                }
            
            # 5. Convertir a entidad ECA
            eca = await self._convertir_preferencia_a_eca(preferencia_request)
            
            # 6. Guardar en repositorio de personalización
            if not await self.repository.guardar_preferencia_usuario(eca, preferencia_request.email):
                return {"error": "Error guardando preferencia", "status_code": 500}
            
            # 7. ENVIAR ECA AL MICROSERVICIO DE AUTOMATIZACIÓN
            resultado_automatizacion = await self._enviar_eca_a_automatizacion(eca)
            
            if not resultado_automatizacion.get("exito", False):
                logger.warning(f"ECA guardado en personalización pero error en automatización: {resultado_automatizacion.get('error')}")
                # Podemos decidir si fallar completamente o solo warning
                # Por ahora continuamos ya que la preferencia se guardó
            
            return {
                "mensaje": "Preferencia creada correctamente",
                "eca_creado": eca.name_eca,
                "automatizacion": resultado_automatizacion,
                "status_code": 200
            }
            
        except Exception as e:
            logger.error(f"Error creando preferencia: {e}")
            return {"error": "Error interno del servidor", "status_code": 500}

    async def procesar_salida_usuario(self, osid: str) -> Dict[str, Any]:
        """Procesa la salida de un usuario - SOLO lógica de personalización"""
        try:
            logger.info(f"Procesando salida de usuario: {osid}")
            
            # 1. Obtener email asociado al osid
            email = await self._obtener_email_por_osid(osid)
            
            if not email:
                return {"error": "Usuario no encontrado", "status_code": 404}
            
            # 2. Limpiar preferencias temporales/caché del usuario
            preferencias_limpiadas = await self.repository.limpiar_preferencias_temporales(email)
            
            # 3. Registrar evento de salida para analytics
            await self._registrar_evento_salida(email, osid)
            
            return {
                "usuario": email,
                "osid": osid,
                "preferencias_limpiadas": preferencias_limpiadas,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error procesando salida de usuario {osid}: {e}")
            return {"error": f"Error procesando salida: {str(e)}", "status_code": 500}

    async def registrar_interaccion(self, email: str, id_data_stream: str, comando: str, osid: str, mac: str, date_interaction: str) -> Dict[str, Any]:
        try:
            logger.info(f"🔄 Registrando interacción: {email} -> {osid}")
            
            # 1. Preparar datos de interacción
            interaccion_data = {
                "email": email,
                "id_data_stream": id_data_stream,
                "comando": comando,
                "objeto_id": osid,
                "dispositivo_mac": mac,
                "fecha_interaccion": date_interaction,
                "timestamp_procesamiento": datetime.now().isoformat()
            }
            
            # 2. Guardar en repositorio de personalización
            interaccion_id = await self.repository.guardar_interaccion(interaccion_data)
            
            # 3. Actualizar perfil de usuario basado en interacción
            perfil_actualizado = await self._actualizar_perfil_usuario(interaccion_data)
            
            return {
                "interaccion_registrada": True,
                "interaccion_id": interaccion_id,
                "perfil_actualizado": perfil_actualizado,
                "data": interaccion_data,
                "status_code": 200
            }
    
        except Exception as e:
            logger.error(f"Error registrando interacción: {e}")
            return {"error": f"Error registrando interacción: {str(e)}", "status_code": 500}
    # ========== MÉTODOS DE COMUNICACIÓN CON OTROS MICROSERVICIOS ==========

    async def _validar_recursos_con_ontologia(self, contrato: Dict[str, Any], osid_origen: str, osid_destino: str) -> Dict[str, Any]:
        """Valida que los recursos del contrato existan en la ontología"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint que necesitamos del microservicio de ontologías
                response = await client.post(
                    f"{settings.ONTOLOGIAS_MS_URL}/ontologias/validar-recursos",
                    json={
                        "contrato": contrato,
                        "osid_origen": osid_origen,
                        "osid_destino": osid_destino
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Error validando recursos con ontología: {response.status_code}")
                    return {"valido": False, "error": f"Error en validación: {response.text}"}
                    
        except httpx.RequestError as e:
            logger.warning(f"Microservicio de ontologías no disponible para validación: {e}")
            # En desarrollo, podríamos simular validación exitosa
            # En producción, deberíamos fallar o tener un modo degradado
            return {"valido": True, "advertencia": "Validación omitida - servicio no disponible"}
    
    async def _enviar_eca_a_automatizacion(self, eca: ECA) -> Dict[str, Any]:
        """Envía el ECA al microservicio de automatización para su gestión"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.AUTOMATIZACION_MS_URL}/automatizacion/ecas",
                    json=eca.to_legacy_dict(),
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    return {"exito": True, "eca_id": response.json().get("id")}
                else:
                    return {"exito": False, "error": f"Error {response.status_code}: {response.text}"}
                    
        except httpx.RequestError as e:
            logger.error(f"Error enviando ECA a automatización: {e}")
            return {"exito": False, "error": "Servicio de automatización no disponible"}

    async def obtener_informacion_ontologia_para_usuario(self, email: str) -> Dict[str, Any]:
        """Obtiene información de ontología relevante para un usuario específico"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.ONTOLOGIAS_MS_URL}/ontologias/info-usuario",
                    params={"email": email},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": "No se pudo obtener información de ontología"}
                    
        except httpx.RequestError:
            return {"error": "Servicio de ontologías no disponible"}

    # ========== MÉTODOS AUXILIARES DE PERSONALIZACIÓN ==========

    async def _verificar_usuario(self, email: str) -> bool:
        """Verifica si el usuario existe - SIMULADO"""
        # En producción, conectar con servicio de autenticación
        logger.info(f"✅ Verificación de usuario simulada para: {email}")
        return True

    def _validar_contrato_basico(self, contrato: Dict[str, Any]) -> bool:
        """Valida estructura básica del contrato"""
        if not isinstance(contrato, dict):
            return False
        
        campos_obligatorios = ['evento', 'accion']
        if not all(campo in contrato for campo in campos_obligatorios):
            return False
        
        evento = contrato.get('evento', {})
        accion = contrato.get('accion', {})
        
        return all([
            'recurso' in evento,
            'operador' in evento,
            'valor' in evento,
            'recurso' in accion,
            'valor' in accion
        ])

    async def _existe_preferencia_duplicada(self, preferencia_request) -> bool:
        """Verifica si ya existe una preferencia similar"""
        # Lógica para detectar duplicados basada en email, osid y osidDestino
        preferencias_usuario = await self.repository.obtener_preferencias_usuario(preferencia_request.email)
        
        for pref in preferencias_usuario:
            if (pref.get('osid') == preferencia_request.osid and 
                pref.get('osidDestino') == preferencia_request.osidDestino and
                pref.get('contrato') == preferencia_request.contrato):
                return True
        return False

    async def _convertir_preferencia_a_eca(self, preferencia_request) -> ECA:
        """Convierte una preferencia a entidad ECA"""
        contrato = preferencia_request.contrato
        
        evento = EventoECA(
            objEvento=preferencia_request.osid,
            id_event_resource=contrato['evento']['recurso'],
            name_event_resource=contrato['evento'].get('nombre_recurso', ''),
            name_event_object=contrato['evento'].get('nombre_objeto', ''),
            signCondicion=contrato['evento'].get('descripcion', ''),
            unidadCondicion=contrato['evento'].get('unidad', ''),
            variableCondicion=str(contrato['evento']['valor']),
            comparadorCondicion=contrato['evento']['operador']
        )
        
        accion = AccionECA(
            objAccion=preferencia_request.osidDestino,
            id_action_resource=contrato['accion']['recurso'],
            name_action_resource=contrato['accion'].get('nombre_recurso', ''),
            name_action_object=contrato['accion'].get('nombre_objeto', ''),
            signAccion=contrato['accion'].get('descripcion', ''),
            unidadAccion=contrato['accion'].get('unidad', ''),
            variableAccion=str(contrato['accion']['valor']),
            comparadorAccion=contrato['accion'].get('operador', 'igual')
        )
        
        # Generar nombre único para el ECA
        preferencias_count = len(await self.repository.obtener_preferencias_usuario(preferencia_request.email))
        nombre_eca = f"eca_{preferencia_request.email}_{preferencias_count + 1}"
        
        return ECA(
            name_eca=nombre_eca,
            eca_state="on",  # Por defecto activado
            eventoECA=evento,
            accionECA=accion,
            user_eca=preferencia_request.email
        )

    async def _obtener_email_por_osid(self, osid: str) -> str:
        """Obtiene email asociado a OSID - SIMULADO"""
        if osid.startswith("usuario_"):
            return f"{osid}@ejemplo.com"
        return f"usuario_{osid}@ejemplo.com"

    async def _registrar_evento_salida(self, email: str, osid: str):
        """Registra evento de salida para analytics"""
        logger.info(f"📝 Registrando evento de salida: {email} (osid: {osid})")
        # En producción, enviar a sistema de analytics

    async def _actualizar_perfil_usuario(self, interaccion_data: Dict[str, Any]) -> bool:
        """Actualiza el perfil de usuario basado en la interacción"""
        # Lógica para actualizar preferencias, hábitos, etc.
        logger.info(f"🔄 Actualizando perfil para: {interaccion_data['email']}")
        return True

    async def _generar_sugerencias_preferencias(self, interaccion_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera sugerencias de preferencias basadas en interacciones"""
        # Lógica de machine learning/recomendaciones
        logger.info("💡 Generando sugerencias de preferencias")
        return []