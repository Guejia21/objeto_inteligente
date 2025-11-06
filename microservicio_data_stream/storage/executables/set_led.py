# Controla un LED

def main(comparador, valor):
    """
    Args:
        comparador: "igual", "mayor", "menor"
        valor: valor a establecer
    """
    print(f"LED: {comparador} {valor}")
    
    # Aquí irías tu código para controlar el LED
    # Ejemplo con machine (ESP32/Pico):
    # from machine import Pin
    # led = Pin(2, Pin.OUT)
    # 
    # if valor == "1" or valor.lower() == "on":
    #     led.on()
    # else:
    #     led.off()