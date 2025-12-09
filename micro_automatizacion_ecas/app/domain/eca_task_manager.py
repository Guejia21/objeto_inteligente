"""Gestor de tareas ECA que escucha telemetría MQTT"""
import asyncio
import json
from typing import Dict, Optional
from domain.eca_evaluator import ECAEvaluator
from infra.logging.Logging import logger
from infra.logging.ILogPanelMQTT import ILogPanelMQTT
from config import settings


class ECATaskManager:
    """Gestiona las tareas de monitoreo de ECAs"""
    
    def __init__(self):
        self.active_ecas: Dict[str, ECAEvaluator] = {}
        self.broker: Optional[ILogPanelMQTT] = None
        self.telemetry_topic = settings.MQTT_TELEMETRY_TOPIC
        self.is_listening = False
        self._listener_started = asyncio.Event()
    
    def set_broker(self, broker: ILogPanelMQTT):
        """Configura el broker MQTT a usar"""
        self.broker = broker
        logger.info("Broker MQTT configurado en ECATaskManager")
    
    async def register_eca(self, eca_config: Dict) -> bool:
        """
        Registra un nuevo ECA para monitoreo
        """
        try:
            eca_name = eca_config.get("name_eca", "")
            user_eca = eca_config.get("user_eca", "default")
            eca_key = f"{eca_name}_{user_eca}"
            
            # Crear evaluador
            evaluator = ECAEvaluator(eca_config)
            self.active_ecas[eca_key] = evaluator
            
            logger.info(f"ECA registrado: {eca_key} (estado: {evaluator.state})")
            
            # Iniciar listener si es el primer ECA activo
            if evaluator.state == "on" and not self.is_listening:
                await self._start_telemetry_listener()
            
            return True
            
        except Exception as e:
            logger.error(f"Error registrando ECA: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def unregister_eca(self, eca_name: str, user_eca: str = "default") -> bool:
        """Elimina un ECA del monitoreo"""
        eca_key = f"{eca_name}_{user_eca}"
        
        if eca_key in self.active_ecas:
            del self.active_ecas[eca_key]
            logger.info(f"ECA eliminado del monitoreo: {eca_key}")
            return True
        return False
    
    async def update_eca_state(self, eca_name: str, new_state: str, user_eca: str = "default"):
        """Actualiza el estado (on/off) de un ECA existente"""        
        eca_key = f"{eca_name}_{user_eca}"
        
        if eca_key in self.active_ecas.keys():
            self.active_ecas[eca_key].state = new_state
            logger.info(f"ECA {eca_key} cambió a estado: {new_state} en gestor de tareas")
            
            if new_state == "on" and not self.is_listening:
                await self._start_telemetry_listener()
            return         
        logger.warning(f"ECA {eca_key} no encontrado para actualizar estado")
    
    async def _start_telemetry_listener(self):
        """Inicia la suscripción al tópico de telemetría"""
        if self.is_listening or not self.broker:
            logger.warning(f"No se puede iniciar listener: is_listening={self.is_listening}, broker={self.broker is not None}")
            return
        
        self.is_listening = True
        logger.info(f"Iniciando listener de telemetría en: {self.telemetry_topic}")
        
        # Callback async directo - NO usar run_coroutine_threadsafe aquí
        async def on_telemetry(topic: str, message: str):
            """Callback async cuando llega un mensaje de telemetría"""
            #logger.debug(f"Telemetría recibida en topic {topic}")
            await self._process_telemetry_message(message)
        
        try:
            await self.broker.suscribir(self.telemetry_topic, on_telemetry)
            self._listener_started.set()
            logger.info("Listener de telemetría iniciado correctamente")
        except Exception as e:
            logger.error(f"Error iniciando listener: {e}")
            self.is_listening = False
    
    async def _process_telemetry_message(self, message: str):
        """Procesa un mensaje de telemetría y evalúa todos los ECAs activos"""
        try:
            #logger.debug(f"Procesando mensaje de telemetría: {message}")
            telemetry = json.loads(message)
            
            if not self.active_ecas:
                #logger.debug("No hay ECAs activos para procesar")
                return
            
            for eca_key, evaluator in self.active_ecas.items():
                if evaluator.state != "on":
                    continue
                
                should_execute = evaluator.process_telemetry(telemetry)
                expected_action = "on" if evaluator.action_value else "off"
                if should_execute:
                    if evaluator.last_action_executed != expected_action:
                        logger.info(f"ECA [{eca_key}]: Condición cumplida, ejecutando acción...")
                        await evaluator.execute_action()
                else:
                    # La condición ya no se cumple, revertir acción si fue ejecutada
                    if evaluator.last_action_executed == expected_action:
                        logger.info(f"ECA [{eca_key}]: La condición dejo de cumplirse, revirtiendo acción...")
                        await evaluator.execute_inverse_action()
                        
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando telemetría: {e}")
        except Exception as e:
            logger.error(f"Error procesando telemetría: {e}")
            import traceback
            traceback.print_exc()
    
    def get_active_ecas(self) -> Dict[str, Dict]:
        """Retorna información de todos los ECAs activos"""
        return {
            key: {
                "eca_name": e.name,
                "eca_state": e.state,
                "user_eca": e.user_eca,
                "event_resource": e.event_resource_id,
                "action_resource": e.action_resource_id,
                "threshold": e.threshold_value,
                "comparator": e.comparator
            }
            for key, e in self.active_ecas.items()
        }    


# Instancia global
eca_task_manager = ECATaskManager()