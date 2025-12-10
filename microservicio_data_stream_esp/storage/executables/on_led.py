"""
Ejecutable: Encender LED
Datastream: led_status
Action: write (ON)
"""

from machine import Pin

# Configuración del LED
LED_GPIO = 2  # GPIO2 - LED integrado ESP32

# Inicializar pin si no existe (compartido entre scripts)
if 'led_pin' not in pins:
    pins['led_pin'] = Pin(LED_GPIO, Pin.OUT)
    print(f"✅ LED inicializado en GPIO{LED_GPIO}")

# Encender LED
pins['led_pin'].value(1)

# Resultado que se retorna al servicio
result = {
    'success': True,
    'datastream_id': 'led_status',
    'action': 'write',
    'operation': 'on',
    'value': True,
    'gpio': LED_GPIO,
    'message': 'LED encendido'
}

print(f"💡 LED ON (GPIO{LED_GPIO})")