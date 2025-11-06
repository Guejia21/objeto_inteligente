try:
    from hardware.gpio_adapter import gpio
    
    # Pin D3 en GrovePi = GPIO 2 en ESP32 (ajusta según tu conexión)
    LED_PIN = 3  # D3 en Raspberry, cambiar a 2 para ESP32
    
    # Encender LED
    gpio.digital_write(LED_PIN, 1)
    print("LED encendido")
    
except Exception as e:
    print(f"Error: {e}")