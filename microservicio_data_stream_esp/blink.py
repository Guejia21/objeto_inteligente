"""
Programa de prueba ESP32: Parpadear LED y mostrar info
"""

from machine import Pin, unique_id
import time
import ubinascii

# Configuración
LED_PIN = 2  # GPIO2 (cambia a 5 si no funciona)
BLINK_INTERVAL = 0.5  # segundos

# Obtener ID único del ESP32
chip_id = ubinascii.hexlify(unique_id()).decode()

print("=" * 40)
print("🚀 ESP32 MicroPython - Test Program")
print("=" * 40)
print(f"Chip ID: {chip_id}")
print(f"LED GPIO: {LED_PIN}")
print(f"Blink Interval: {BLINK_INTERVAL}s")
print("=" * 40)
print("Presiona Ctrl+C para detener\n")

# Inicializar LED
led = Pin(LED_PIN, Pin.OUT)
led.value(0)  # Apagar al inicio

# Contador
count = 0

try:
    while True:
        # Encender LED
        led.value(1)
        print(f"[{count:04d}] 💡 LED ON  - {time.ticks_ms()}ms")
        time.sleep(BLINK_INTERVAL)
        
        # Apagar LED
        led.value(0)
        print(f"[{count:04d}] ⚫ LED OFF - {time.ticks_ms()}ms")
        time.sleep(BLINK_INTERVAL)
        
        count += 1
        
        # Cada 10 parpadeos, mostrar memoria
        if count % 10 == 0:
            import gc
            gc.collect()
            print(f"📊 Memoria libre: {gc.mem_free()} bytes\n")

except KeyboardInterrupt:
    print("\n❌ Programa detenido por el usuario")
    led.value(0)  # Apagar LED al salir
    print("👋 Adiós!")