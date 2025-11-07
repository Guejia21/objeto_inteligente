"""try:
    from hardware.gpio_adapter import gpio
    
    LED_PIN = 3  # D3 en Raspberry, GPIO 2 en ESP32
    
    # Apagar LED
    gpio.digital_write(LED_PIN, 0)
    print("LED apagado")
    
except Exception as e:
    print(f"Error: {e}")"""
#Mientras se arregla la grove pi, se simulan los valores
print("LED apagado")