"""
Ejecutable: Apagar LED
Datastream: led_status
Action: write (OFF)
"""

from machine import Pin

# Configuración del LED
LED_GPIO = 2

# Inicializar pin si no existe
if 'led_pin' not in pins:
    pins['led_pin'] = Pin(LED_GPIO, Pin.OUT)
    print(f"✅ LED inicializado en GPIO{LED_GPIO}")

# Apagar LED
pins['led_pin'].value(0)

# Resultado
result = {
    'success': True,
    'datastream_id': 'led_status',
    'action': 'write',
    'operation': 'off',
    'value': False,
    'gpio': LED_GPIO,
    'message': 'LED apagado'
}

print(f"⚫ LED OFF (GPIO{LED_GPIO})")