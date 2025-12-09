"""Evaluador de condiciones ECA"""
import httpx
from typing import Dict, Any, Callable
from infra.logging.Logging import logger


class ECAEvaluator:
    """Evalúa condiciones ECA y ejecuta acciones cuando se cumplen"""
    
    COMPARATORS = {
        "mayor": lambda a, b: a > b,
        "menor": lambda a, b: a < b,
        "igual": lambda a, b: a == b,
        "mayor_igual": lambda a, b: a >= b,
        "menor_igual": lambda a, b: a <= b,
        "diferente": lambda a, b: a != b,
    }
    
    def __init__(self, eca_config: Dict[str, Any]):
        """
        Inicializa el evaluador con la configuración del ECA
        
        Args:
            eca_config: Diccionario del eca (obtenido de getDiccionarioECA)
        """
        self.config = eca_config
        self.name = eca_config.get("name_eca", "ECA_Sin_Nombre")
        self.state = eca_config.get("state_eca", "off")
        self.user_eca = eca_config.get("user_eca", "default")
        
        # Evento
        self.event_object_id = eca_config.get("id_event_object", "")
        self.event_object_ip = eca_config.get("ip_event_object", "")
        self.event_resource_id = eca_config.get("id_event_resource", "")
        
        # Condición
        self.comparator = eca_config.get("comparator_condition", "igual")
        self.threshold_value = self._parse_value(
            eca_config.get("variable_condition"),
            eca_config.get("type_variable_condition", "string")
        )
        
        # Acción
        self.action_object_id = eca_config.get("id_action_object", "")
        self.action_object_ip = eca_config.get("ip_action_object", "")
        self.action_resource_id = eca_config.get("id_action_resource", "")
        self.action_value = self._parse_value(
            eca_config.get("variable_action"),
            eca_config.get("type_variable_action", "string")
        )
        self.action_comparator = eca_config.get("comparator_action", "igual")
        
        # Estado interno
        self.last_action_executed = None
        self.is_running = False
        
    def _parse_value(self, value: Any, value_type: str) -> Any:
        """Convierte el valor al tipo correcto"""
        if value is None:
            return None
        try:
            if value_type == "float":
                return float(value)
            elif value_type == "int":
                return int(value)
            elif value_type == "bool":
                return value in [True, "true", "True", "1", 1, "on", "ON"]
            else:
                return str(value)
        except (ValueError, TypeError):
            return value
    
    def evaluate_condition(self, sensor_value: Any) -> bool:
        """
        Evalúa si la condición del ECA se cumple
        
        Args:
            sensor_value: Valor actual del sensor
            
        Returns:
            True si la condición se cumple, False en caso contrario
        """
        if self.state != "on":
            return False
            
        comparator_func = self.COMPARATORS.get(self.comparator)
        if not comparator_func:
            logger.warning(f"Comparador desconocido: {self.comparator}")
            return False
        
        try:
            # Convertir sensor_value al mismo tipo que threshold para que la comparación sea válida
            if isinstance(self.threshold_value, float):
                sensor_value = float(sensor_value)
            elif isinstance(self.threshold_value, int):
                sensor_value = int(sensor_value)
            elif isinstance(self.threshold_value, bool):
                sensor_value = sensor_value in [True, "true", "True", "1", 1]
            #logger.info(f"Evaluando condición: {sensor_value} {self.comparator} {self.threshold_value}")
            result = comparator_func(sensor_value, self.threshold_value)
            return result
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error comparando valores: {e}")
            return False
    
    async def execute_action(self) -> bool:
        """
        Ejecuta la acción del ECA via HTTP
        
        Returns:
            True si la acción se ejecutó correctamente
        """
        # Determinar el comando basado en el comparador de acción
        if self.action_comparator == "igual":
            if isinstance(self.action_value, bool):
                comando = "on" if self.action_value else "off"
            else:
                comando = "set"
        else:
            comando = "set"
        
        # Construir URL del objeto acción
        url = f"http://{self.action_object_ip}:8003/Datastreams/SetDatastream?osid={self.action_object_id}&idDataStream={self.action_resource_id}&comando={comando}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if comando == "set":
                    # Para set, enviar el valor en el body
                    response = await client.post(url, json={"value": self.action_value})
                else:
                    # Para on/off, solo hacer POST
                    response = await client.post(url)
                
                if response.status_code == 200:
                    logger.info(f"ECA [{self.name}]: Acción ejecutada - {comando} en {self.action_resource_id}")
                    self.last_action_executed = comando
                    return True
                else:
                    logger.error(f"ECA [{self.name}]: Error HTTP {response.status_code}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"ECA [{self.name}]: Timeout conectando a {self.action_object_ip}")
            return False
        except Exception as e:
            logger.error(f"ECA [{self.name}]: Error ejecutando acción: {e}")
            return False
    async def execute_inverse_action(self) -> bool:
        """
        Ejecuta la acción inversa del ECA via HTTP
        
        Returns:
            True si la acción inversa se ejecutó correctamente
        """
        if self.last_action_executed is None:
            return False
        
        # Determinar el comando inverso
        if self.last_action_executed == "on":
            comando = "off"
        elif self.last_action_executed == "off":
            comando = "on"
        else:
            # Para "set", no hay acción inversa definida
            return False
        
        # Construir URL del objeto acción
        url = f"http://{self.action_object_ip}:8003/Datastreams/SetDatastream?osid={self.action_object_id}&idDataStream={self.action_resource_id}&comando={comando}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url)
                
                if response.status_code == 200:
                    logger.info(f"ECA [{self.name}]: Acción inversa ejecutada - {comando} en {self.action_resource_id}")
                    self.last_action_executed = comando
                    return True
                else:
                    logger.error(f"ECA [{self.name}]: Error HTTP {response.status_code} en acción inversa")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"ECA [{self.name}]: Timeout conectando a {self.action_object_ip} en acción inversa")
            return False
        except Exception as e:
            logger.error(f"ECA [{self.name}]: Error ejecutando acción inversa: {e}")
            return False
        
    def process_telemetry(self, telemetry: Dict[str, Any]) -> bool:
        """
        Procesa un mensaje de telemetría y evalúa si debe ejecutar la acción
        
        Args:
            telemetry: Diccionario con los valores de telemetría
            
        Returns:
            True si se debe ejecutar la acción
        """
        # Verificar si el recurso del evento está en la telemetría
        if self.event_resource_id not in telemetry:
            return False
        
        sensor_value = telemetry[self.event_resource_id]
        return self.evaluate_condition(sensor_value)