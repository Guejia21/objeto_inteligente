"""
Ejecutable: Obtener estado del LED
Datastream: led_status
Action: read
"""

from machine import Pin

# Configuración del LED
LED_GPIO = 2

# Inicializar pin si no existe
if 'led_pin' not in pins:
    pins['led_pin'] = Pin(LED_GPIO, Pin.OUT)
    print(f"✅ LED inicializado en GPIO{LED_GPIO}")

# Obtener estado actual
current_state = bool(pins['led_pin'].value())

# Resultado
result = {
    'success': True,
    'datastream_id': 'led_status',
    'action': 'read',
    'value': current_state,
    'gpio': LED_GPIO,
    'message': f"LED {'encendido' if current_state else 'apagado'}"
}

print(f"📊 LED status: {'ON' if current_state else 'OFF'}")