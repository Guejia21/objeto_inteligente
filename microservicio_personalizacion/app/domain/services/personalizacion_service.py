import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile
import os

from app.domain.entities.usuario import Usuario
from app.domain.entities.preferencia import Preferencia
from app.domain.entities.eca import ECA, EventoECA, AccionECA
from app.domain.repositories.personalizacion_repository import PersonalizacionRepository  

logger = logging.getLogger(__name__)

class PersonalizacionService:
    def __init__(self, repository: PersonalizacionRepository):
        self.repository = repository
        self.ontologia_cargada = False
        self.ontologia_actual = None

    async def cargar_ontologia(self, file_content: bytes, nombre: str, ip_coordinador: str) -> Dict[str, Any]:
        """
        Carga y arranca una ontología - Similar a CargarOntologia del legacy
        """
        try:
            logger.info(f"Iniciando carga de ontología: {nombre} desde {ip_coordinador}")
            
            # 1. Guardar archivo temporal (similar al legacy)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.owl') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # 2. Cargar ontología con owlready2 (como en legacy)
            try:
                from owlready2 import get_ontology
                ontologia = get_ontology(temp_path).load()
                logger.info(f"✅ Ontología {nombre} cargada exitosamente")
                
                # 3. Preparar entorno y hilos (como en Starter/Main del legacy)
                await self._preparar_entorno_ontologia(ontologia, ip_coordinador)
                
                self.ontologia_actual = ontologia
                self.ontologia_cargada = True
                
                # 4. Cargar metadata XML auxiliar si existe
                await self._cargar_metadata_auxiliar(ip_coordinador)
                
                return {
                    "estado": "cargada_exitosamente",
                    "nombre": nombre,
                    "ip_coordinador": ip_coordinador,
                    "clases_cargadas": len(list(ontologia.classes())),
                    "individuos_cargados": len(list(ontologia.individuals()))
                }
                
            except ImportError:
                logger.warning("owlready2 no disponible, usando modo simulación")
                return await self._simular_carga_ontologia(nombre, ip_coordinador)
                
            finally:
                # Limpiar archivo temporal
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"❌ Error cargando ontología {nombre}: {e}")
            return {"error": f"Error cargando ontología: {str(e)}", "status_code": 500}

    async def procesar_ontologia(self, file_content: bytes, nombre: str, ip_coordinador: str) -> Dict[str, Any]:
        """
        Procesa una ontología recibida - Para endpoint /RecibirOntologia
        """
        return await self.cargar_ontologia(file_content, nombre, ip_coordinador)

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
            
            # 5. Poblar ECA en ontología (similar a poblarEca del legacy)
            if self.ontologia_cargada:
                eca_ontologia = await self._poblar_eca_ontologia(eca, preferencia.contrato)
                if not eca_ontologia:
                    return {"error": "Error poblando ECA en ontología", "status_code": 500}
            
            # 6. Guardar en repositorio
            if not await self.repository.guardar_eca(eca):
                return {"error": "Error interno del servidor", "status_code": 500}
            
            # 7. Iniciar ejecución ECA (similar a Modelo/ECA.py del legacy)
            await self._iniciar_ejecucion_eca(eca)
            
            # 8. Publicar evento (si está configurado)
            await self._publicar_evento_preferencia_creada(preferencia, eca)
            
            return {"mensaje": "Contrato creado correctamente", "status_code": 200}
            
        except Exception as e:
            logger.error(f"Error creando preferencia: {e}")
            return {"error": "Error interno del servidor", "status_code": 500}

    async def _poblar_eca_ontologia(self, eca: ECA, contrato: Dict[str, Any]) -> bool:
        """
        Pobla un ECA en la ontología - Similar a PoblarECA.py del legacy
        """
        try:
            if not self.ontologia_actual:
                logger.warning("Ontología no cargada, no se puede poblar ECA")
                return False
            
            # Obtener clases de la ontología (como en legacy)
            ClaseECA = self.ontologia_actual.search_one(iri="*ECA")
            ClaseEvento = self.ontologia_actual.search_one(iri="*Evento")
            ClaseCondicion = self.ontologia_actual.search_one(iri="*Condicion")
            ClaseAccion = self.ontologia_actual.search_one(iri="*Accion")
            
            if not all([ClaseECA, ClaseEvento, ClaseCondicion, ClaseAccion]):
                logger.error("Clases ECA no encontradas en ontología")
                return False
            
            # Crear individuos (como en PoblarECA.py)
            # 1. Crear Evento
            individuo_evento = ClaseEvento(f"evento_{eca.name_eca}")
            individuo_evento.id_event_resource = [contrato['evento']['recurso']]
            individuo_evento.name_event_resource = [contrato['evento'].get('nombre_recurso', '')]
            individuo_evento.name_event_object = [contrato['evento'].get('nombre_objeto', '')]
            individuo_evento.signCondicion = [contrato['evento'].get('descripcion', '')]
            individuo_evento.unidadCondicion = [contrato['evento'].get('unidad', '')]
            individuo_evento.variableCondicion = [str(contrato['evento']['valor'])]
            individuo_evento.comparadorCondicion = [contrato['evento']['operador']]
            
            # 2. Crear Condición
            individuo_condicion = ClaseCondicion(f"condicion_{eca.name_eca}")
            individuo_condicion.is_related_with = [individuo_evento]
            
            # 3. Crear Acción
            individuo_accion = ClaseAccion(f"accion_{eca.name_eca}")
            individuo_accion.id_action_resource = [contrato['accion']['recurso']]
            individuo_accion.name_action_resource = [contrato['accion'].get('nombre_recurso', '')]
            individuo_accion.name_action_object = [contrato['accion'].get('nombre_objeto', '')]
            individuo_accion.signAccion = [contrato['accion'].get('descripcion', '')]
            individuo_accion.unidadAccion = [contrato['accion'].get('unidad', '')]
            individuo_accion.variableAccion = [str(contrato['accion']['valor'])]
            individuo_accion.comparadorAccion = [contrato['accion'].get('operador', 'igual')]
            
            # 4. Crear ECA
            individuo_eca = ClaseECA(eca.name_eca)
            individuo_eca.eca_state = ["on"]  # Por defecto activado
            individuo_eca.starts_with = [individuo_evento]
            individuo_eca.user_eca = [eca.user_eca]
            
            # Establecer relaciones object properties
            individuo_evento.check = [individuo_condicion]
            individuo_condicion.is_related_with = [individuo_accion]
            
            logger.info(f"✅ ECA {eca.name_eca} poblado en ontología")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error poblando ECA en ontología: {e}")
            return False

    async def cambiar_estado_eca(self, osid: str, nombre_eca: str, estado: str) -> Dict[str, Any]:
        """Cambia estado de un ECA (similar a SetEcaState del legacy)"""
        try:
            if estado not in ["on", "off"]:
                return {"error": "estado inválido", "status_code": 400}
            
            # 1. Cambiar en ontología si está cargada
            if self.ontologia_cargada:
                await self._cambiar_estado_eca_ontologia(nombre_eca, estado)
            
            # 2. Cambiar en repositorio
            if await self.repository.cambiar_estado_eca(nombre_eca, estado):
                # 3. Orquestar ciclo de vida (similar a Modelo/ECA.py)
                await self._orquestar_ciclo_vida_eca(nombre_eca, estado)
                return {"mensaje": f"ECA {nombre_eca} {estado}", "status_code": 200}
            else:
                return {"error": "Error cambiando estado del ECA", "status_code": 500}
                
        except Exception as e:
            logger.error(f"Error cambiando estado del ECA {nombre_eca}: {e}")
            return {"error": "Error interno del servidor", "status_code": 500}

    async def _cambiar_estado_eca_ontologia(self, nombre_eca: str, estado: str):
        """
        Cambia estado de ECA en ontología - Similar a ConsultasOOS.setEcaState
        """
        try:
            if not self.ontologia_actual:
                return
            
            # Buscar individuo ECA
            individuo_eca = self.ontologia_actual.search_one(iri=f"*{nombre_eca}")
            if individuo_eca:
                individuo_eca.eca_state = [estado]
                logger.info(f"Estado de ECA {nombre_eca} cambiado a {estado} en ontología")
        except Exception as e:
            logger.error(f"Error cambiando estado en ontología para {nombre_eca}: {e}")

    async def listar_ecas_usuario(self, email: str, osid: str) -> Dict[str, Any]:
        """Lista ECAs de un usuario (similar a ConsultasOOS.listarEcasUsuario)"""
        try:
            # 1. Obtener del repositorio
            ecas = await self.repository.listar_ecas_usuario(email)
            
            # 2. Si ontología cargada, enriquecer con datos de ontología
            if self.ontologia_cargada:
                ecas = await self._enriquecer_ecas_con_ontologia(ecas)
            
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

    async def desactivar_ecas_por_osid(self, osid: str) -> Dict[str, Any]:
        """
        Desactiva ECAs basado en OSID - Para endpoint /NotificarSalidaDeUsuario
        Similar a ApagarTodosEcas del legacy
        """
        try:
            logger.info(f"Desactivando ECAs para usuario con osid: {osid}")
            
            # 1. Obtener email asociado al osid (simulado)
            email = await self._obtener_email_por_osid(osid)
            
            if not email:
                return {"error": "Usuario no encontrado", "status_code": 404}
            
            # 2. Desactivar en repositorio
            ecas_desactivados = await self.repository.desactivar_ecas_usuario(email)
            
            # 3. Desactivar en ontología si está cargada
            if self.ontologia_cargada:
                for eca_nombre in ecas_desactivados:
                    await self._cambiar_estado_eca_ontologia(eca_nombre, "off")
            
            # 4. Detener ejecución de ECAs (similar a Modelo/ECA.py)
            await self._detener_ejecucion_ecas_usuario(email)
            
            return {
                "mensaje": f"ECAs desactivados para usuario con osid: {osid}",
                "osid": osid,
                "email": email,
                "ecas_desactivados": ecas_desactivados,
                "status_code": 200
            }
            
        except Exception as e:
            logger.error(f"❌ Error desactivando ECAs para osid {osid}: {e}")
            return {"error": f"Error al desactivar ECAs: {str(e)}", "status_code": 500}

    async def registrar_interaccion(self, email: str, id_data_stream: str, comando: str, 
                                  osid: str, mac: str, date_interaction: str) -> Dict[str, Any]:
        """
        Registra interacción usuario-objeto - Para endpoint /RegistroInteraccionUsuarioObjeto
        """
        try:
            logger.info(f"Registrando interacción: {email} -> {osid} - {comando}")
            
            # Lógica para registrar la interacción
            interaccion_data = {
                "email": email,
                "id_data_stream": id_data_stream,
                "comando": comando,
                "objeto_id": osid,
                "dispositivo_mac": mac,
                "fecha_interaccion": date_interaction,
                "timestamp_procesamiento": datetime.now().isoformat()
            }
            
            # Guardar en repositorio
            interaccion_id = await self.repository.guardar_interaccion(interaccion_data)
            
            # Evaluar si esta interacción dispara algún ECA
            await self._evaluar_interaccion_para_ecas(interaccion_data)
            
            return {
                "interaccion_registrada": True,
                "interaccion_id": interaccion_id,
                "data": interaccion_data,
                "status_code": 200
            }
            
        except Exception as e:
            logger.error(f"❌ Error registrando interacción usuario {email} - objeto {osid}: {e}")
            return {"error": f"Error registrando interacción: {str(e)}", "status_code": 500}

    # Métodos auxiliares específicos del legacy
    async def _preparar_entorno_ontologia(self, ontologia, ip_coordinador: str):
        """Prepara entorno y hilos para ontología - Similar a Starter/Main del legacy"""
        logger.info("Preparando entorno de ontología...")
        # Aquí iría la lógica de inicialización de hilos y entorno
        # como en el sistema legacy

    async def _cargar_metadata_auxiliar(self, ip_coordinador: str):
        """Carga metadata XML auxiliar - Similar a legacy"""
        logger.info(f"Cargando metadata auxiliar desde {ip_coordinador}")

    async def _simular_carga_ontologia(self, nombre: str, ip_coordinador: str) -> Dict[str, Any]:
        """Simula carga de ontología cuando owlready2 no está disponible"""
        logger.info(f"Simulando carga de ontología: {nombre}")
        return {
            "estado": "cargada_simulada",
            "nombre": nombre,
            "ip_coordinador": ip_coordinador,
            "clases_cargadas": 15,
            "individuos_cargados": 8
        }

    async def _iniciar_ejecucion_eca(self, eca: ECA):
        """Inicia ejecución de ECA - Similar a Modelo/EjecutarEca.py del legacy"""
        logger.info(f"Iniciando ejecución de ECA: {eca.name_eca}")
        # Aquí iría la lógica de arranque de hilos y monitoreo

    async def _orquestar_ciclo_vida_eca(self, nombre_eca: str, estado: str):
        """Orquesta ciclo de vida ECA - Similar a Modelo/ECA.py del legacy"""
        logger.info(f"Orquestando ciclo de vida para ECA {nombre_eca}: {estado}")

    async def _detener_ejecucion_ecas_usuario(self, email: str):
        """Detiene ejecución de ECAs de usuario - Similar a legacy"""
        logger.info(f"Deteniendo ejecución de ECAs para usuario: {email}")

    async def _evaluar_interaccion_para_ecas(self, interaccion_data: Dict[str, Any]):
        """Evalúa si interacción dispara algún ECA - Similar a EjecutarEcaIndependiente.py"""
        logger.info("Evaluando interacción para posibles ECAs disparados")

    async def _obtener_email_por_osid(self, osid: str) -> Optional[str]:
        """Obtiene email asociado a OSID (simulado)"""
        # En implementación real, consultaría base de datos o servicio
        return f"usuario_{osid}@ejemplo.com"

    async def _enriquecer_ecas_con_ontologia(self, ecas: List[ECA]) -> List[ECA]:
        """Enriquece ECAs con datos de ontología"""
        # Implementación para combinar datos de repositorio y ontología
        return ecas

    # Métodos privados existentes (mantener compatibilidad)
    async def _verificar_usuario(self, usuario: Usuario) -> bool:
        return usuario.verificar_autenticacion()

    async def _existe_eca_duplicado(self, preferencia: Preferencia) -> bool:
        ecas_usuario = await self.repository.listar_ecas_usuario(preferencia.email)
        for eca in ecas_usuario:
            if (eca.eventoECA.objEvento == preferencia.osid and 
                eca.accionECA.objAccion == preferencia.osidDestino):
                return True
        return False

    async def _convertir_preferencia_a_eca(self, preferencia: Preferencia) -> ECA:
        contrato = preferencia.contrato
        
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
        
        nombre_eca = f"eca_{preferencia.email}_{preferencia.osid}_{len(await self.repository.listar_ecas_usuario(preferencia.email)) + 1}"
        
        return ECA(
            name_eca=nombre_eca,
            eca_state="on",
            eventoECA=evento,
            accionECA=accion,
            user_eca=preferencia.email
        )

    async def _publicar_evento_preferencia_creada(self, preferencia: Preferencia, eca: ECA):
        """Publica evento de preferencia creada"""
        pass

    # Métodos del repositorio que deben existir
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