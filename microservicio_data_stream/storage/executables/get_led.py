"""try:
    from hardware.gpio_adapter import gpio
    
    # Pin D3 en GrovePi = GPIO 2 en ESP32 (ajusta según tu conexión)
    LED_PIN = 3  # D3 en Raspberry, cambiar a 2 para ESP32
    # Leer estado LED
    value = gpio.digital_read(LED_PIN)
    print(f"Estado LED: {'Encendido' if value else 'Apagado'}")
except Exception as e:
    print(f"Error: {e}")
"""
#Mientras se arregla la grove pi, se simulan los valores
value = 1  # Simular LED encendido
print(f"Estado LED: {'Encendido' if value else 'Apagado'}")