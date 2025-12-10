"""
Boot script para ESP32 - Configuración inicial del sistema
Se ejecuta antes que main.py
"""

import gc
import esp

print("="*40)
print("  ESP32 DataStream Service")
print("="*40)

# 1. Desactivar debug del ESP para ahorrar RAM
esp.osdebug(None)
print("Debug ESP desactivado")

# 2. Liberar memoria agresivamente
gc.threshold(4096)  # Recolectar basura más frecuentemente
gc.collect()
mem_free = gc.mem_free()
print("Memoria libre: " + str(mem_free) + " bytes")

# 3. NO inicializar WiFi aquí (ahorra ~30KB de RAM)
print("WiFi: Deshabilitado (para ahorrar memoria)")

# 4. Información del sistema
print("\nInformacion del sistema:")
flash_kb = esp.flash_size() // 1024
print("  Flash: " + str(flash_kb) + "KB")

import machine
uid_bytes = machine.unique_id()
uid_hex = ':'.join('%02x' % b for b in uid_bytes)
print("  ID: " + uid_hex)

print("\nBoot completado - Iniciando main.py...")
print("="*40 + "\n")