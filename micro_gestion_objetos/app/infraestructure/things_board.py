"""Cliente de API REST para ThingsBoard"""
import json
import requests
from typing import Optional, Dict
from config import settings
from infraestructure.logging.Logging import logger
class ThingsBoardAPI:
    def __init__(self, host: str = settings.THINGSBOARD_HOST, port: int = settings.THINGSBOARD_PORT):
        self.base_url = f"http://{host}:{port}"
        self.token = None
    
    def login(self, username: str, password: str) -> bool:
        """
        Autentica con ThingsBoard y obtiene el token JWT
        
        Args:
            username: Usuario de ThingsBoard (ej: tenant@thingsboard.org)
            password: Contraseña
            
        Returns:
            True si la autenticación fue exitosa
        """
        url = f"{self.base_url}/api/auth/login"
        payload = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload,timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                settings.THINGSBOARD_ACCESS_TOKEN = self.token  # Guardar token en configuración
                logger.info("Autenticación exitosa")                
                return True
            else:
                logger.error(f"Error de autenticación: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción en login: {e}")
            return False
    
    def create_device(self, device_name: str, device_type: str = "default", 
                     label: str = None) -> Optional[Dict]:
        """
        Crea un nuevo dispositivo en ThingsBoard
        
        Args:
            device_name: Nombre del dispositivo
            device_type: Tipo de dispositivo
            label: Etiqueta opcional
            
        Returns:
            Dict con información del dispositivo creado o None si falla
        """
        if not self.token:
            logger.error("No autenticado. Llama a login() primero")
            return None
        
        url = f"{self.base_url}/api/device"
        headers = {
            "Content-Type": "application/json",
            "X-Authorization": f"Bearer {self.token}"
        }
        
        payload = {
            "name": device_name,
            "type": device_type,
            "label": label or device_name
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers,timeout=10)
            
            if response.status_code == 200:
                device = response.json()
                logger.info(f"Dispositivo '{device_name}' creado exitosamente")
                logger.info(f"   ID: {device.get('id', {}).get('id')}")
                return device
            else:
                logger.error(f"Error creando dispositivo: {response.status_code}")
                logger.error(f"   Respuesta: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción creando dispositivo: {e}")
            return None
    
    def get_device_credentials(self, device_id: str) -> Optional[str]:
        """
        Obtiene las credenciales (Access Token) de un dispositivo
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            Access Token del dispositivo o None si falla
        """
        if not self.token:
            logger.error("No autenticado. Llama a login() primero")
            return None
        
        url = f"{self.base_url}/api/device/{device_id}/credentials"
        headers = {
            "X-Authorization": f"Bearer {self.token}"
        }
        
        try:
            response = requests.get(url, headers=headers,timeout=10)
            
            if response.status_code == 200:
                credentials = response.json()
                access_token = credentials.get("credentialsId")
                logger.info(f"Credenciales obtenidas para dispositivo ID {device_id}")
                return access_token
            else:
                logger.error(f"Error obteniendo credenciales: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción obteniendo credenciales: {e}")
            return None
    
    def create_device_with_token(self, device_name: str, device_type: str = "default") -> Optional[str]:
        """
        Crea un dispositivo y obtiene su Access Token en una sola llamada
        
        Args:
            device_name: Nombre del dispositivo
            device_type: Tipo de dispositivo
            
        Returns:
            Access Token del dispositivo o None si falla
        """
        # Asegurar autenticación
        if self.login(settings.THINGSBOARD_USER, settings.THINGSBOARD_PASSWORD) is False:
            return None
        # Crear dispositivo
        device = self.create_device(device_name, device_type)
        if not device:
            return None
        
        # Obtener credenciales
        device_id = device.get("id", {}).get("id")
        if not device_id:
            logger.error("No se pudo obtener el ID del dispositivo")
            return None
        
        return self.get_device_credentials(device_id)
tb_client = ThingsBoardAPI()