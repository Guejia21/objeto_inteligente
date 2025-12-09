"""
Metadata del objeto inteligente (quemada)
Define los datastreams disponibles
"""

# Metadata del dispositivo
METADATA = {
    "device": {
        "osid": "ObjetoESP32",
        "title": "ESP32 Smart Object",
        "ip": "192.168.8.209",
        "type": "IoT Device",
        "description": "Objeto inteligente con LED y RTC",
        "platform": "ESP32",
        "version": "1.0.0"
    },
    "datastreams": [
        {
            "datastream_id": "led",
            "name": "LED Integrado",
            "description": "Control del LED integrado en GPIO2",
            "datastream_type": "actuator",
            "datastream_format": "boolean",
            "unit": {
                "label": "Estado",
                "symbol": "on/off"
            },
            "gpio": 2,
            "operations": {
                "read": "get_led.py",
                "write_on": "on_led.py",
                "write_off": "off_led.py"
            },
            "current_value": False,
            "tags": ["actuator", "led", "gpio2"]
        },
        
        {
            "datastream_id": "reloj",
            "name": "Reloj RTC",
            "description": "Reloj de tiempo real interno del ESP32",
            "datastream_type": "sensor",
            "datastream_format": "timestamp",
            "unit": {
                "label": "Fecha/Hora",
                "symbol": "datetime"
            },
            "operations": {
                "read": "get_reloj.py",
                "write": "set_reloj.py"
            },
            "current_value": "2024-01-01 00:00:00",
            "tags": ["sensor", "rtc", "time"]
        }
    ]
}


def obtener_metadatos():
    """
    Retorna los metadatos del dispositivo
    Returns:
        dict: Metadata completa
    """
    return METADATA


def obtener_datastream(datastream_id):
    """
    Obtiene un datastream específico por ID
    Args:
        datastream_id: ID del datastream
    Returns:
        dict: Datastream o None si no existe
    """
    for ds in METADATA.get("datastreams", []):
        if ds.get("datastream_id") == datastream_id:
            return ds
    return None


def obtener_datastreams():
    """
    Retorna lista de todos los datastreams
    Returns:
        list: Lista de datastreams
    """
    return METADATA.get("datastreams", [])


def obtener_info_dispositivo():
    """
    Retorna información del dispositivo
    Returns:
        dict: Info del dispositivo
    """
    return METADATA.get("device", {})