try:
    from hardware.gpio_adapter import gpio
    
    # Pin A0 en GrovePi = GPIO 36 en ESP32 (ajusta según la conexión)
    TEMP_PIN = 0  # A0 en Raspberry, cambiar a 36 para ESP32
    
    # Leer temperatura
    value = gpio.read_temperature(TEMP_PIN, '1.2')
    
    print(value)
    
except Exception as e:
    print(f"Error: {e}")