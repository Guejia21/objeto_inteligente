"""Utilidades para manejo de ECAs"""
import json
import os
from typing import Dict, List
from config import settings
from infra.logging.Logging import logger
    
def update_eca_state_json(eca_name: str, user_eca: str, new_state: str) -> bool:
        """Actualiza el estado de un ECA en su archivo JSON"""
        filename = f"ECA_{eca_name}_{user_eca}.json"
        filepath = os.path.join(settings.PATH_ECA, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"Archivo del ECA no encontrado: {filepath}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as fin:
                eca_data = fin.read()
            
            import json
            eca_dict = json.loads(eca_data)
            eca_dict['state_eca'] = new_state
            
            with open(filepath, 'w', encoding='utf-8') as fout:
                fout.write(json.dumps(eca_dict, indent=4))
            
            logger.info(f"ECA {eca_name} actualizado a estado {new_state} en archivo JSON")
            return True
        except Exception as e:
            logger.error(f"Error actualizando el archivo JSON del ECA: {e}")
            return False
def procesar_comando_json_archivo(path: str) -> List[Dict]:
    """
    Lee y procesa un comando desde un archivo JSON.
    
    Equivalente directo a procesarComandoXml(path).
    
    Args:
        path: Ruta al archivo JSON
    
    Returns:
        Lista con diccionario del comando o lista vacía si hay error
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        dic = {
            "id_action_resource": data["id_action_resource"],
            "comparator_action": data["comparator_action"],
            "variable_action": data["variable_action"],
            "type_variable_action": data["type_variable_action"]
        }
        
        return [dic]
        
    except FileNotFoundError:
        print(f"Archivo no encontrado: {path}")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error procesando archivo JSON: {e}")
        return []