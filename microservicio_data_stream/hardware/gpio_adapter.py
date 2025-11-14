"""
Adaptador de GPIO para soportar Raspberry Pi (desarrollo) y ESP32 (producción)
"""
import sys

# Detectar plataforma
try:
    import machine  # Disponible en ESP32 con MicroPython
    PLATFORM = 'ESP32'
except ImportError:
    PLATFORM = 'RASPBERRY'

class GPIOAdapter:
    """Abstracción de GPIO compatible con Raspberry Pi y ESP32"""
    
    def __init__(self):
        self.platform = PLATFORM
        
        if self.platform == 'ESP32':
            import machine
            self.Pin = machine.Pin
            self.ADC = machine.ADC
        else:
            # Raspberry Pi con Python regular
            try:
                import grovepi
                self.grovepi = grovepi
            except ImportError:
                print("Warning: grovepi no disponible")
                self.grovepi = None
    
    def digital_write(self, pin, value):
        """Escribir valor digital (LED)"""
        if self.platform == 'ESP32':
            p = self.Pin(pin, self.Pin.OUT)
            p.value(value)
        else:
            if self.grovepi:
                self.grovepi.pinMode(pin, "OUTPUT")
                self.grovepi.digitalWrite(pin, value)
    
    def digital_read(self, pin):
        """Leer valor digital"""
        if self.platform == 'ESP32':
            p = self.Pin(pin, self.Pin.IN)
            return p.value()
        else:
            if self.grovepi:
                self.grovepi.pinMode(pin, "INPUT")
                return self.grovepi.digitalRead(pin)
            return 0
    
    def analog_read(self, pin):
        """Leer valor analógico (0-4095 en ESP32, 0-1023 en Raspberry)"""
        if self.platform == 'ESP32':
            adc = self.ADC(self.Pin(pin))
            adc.atten(self.ADC.ATTN_11DB)  # Rango completo 0-3.3V
            return adc.read()
        else:
            if self.grovepi:
                return self.grovepi.analogRead(pin)
            return 0
    
    def read_temperature(self, pin, sensor_type='1.2'):
        """Leer temperatura (Grove Temperature Sensor)"""
        if self.platform == 'ESP32':
            # ESP32: calcular temperatura desde ADC
            # Fórmula para Grove Temperature Sensor v1.2
            adc_value = self.analog_read(pin)
            # Convertir ADC a temperatura (ajusta según tu sensor)
            resistance = (4095.0 / adc_value) - 1.0
            resistance = 100000.0 * resistance
            temperature = 1.0 / (0.001129148 + (0.000234125 * 
                          (resistance / 100000.0)) + 
                          (0.0000000876741 * (resistance / 100000.0) ** 3))
            temperature = temperature - 273.15  # Kelvin a Celsius
            return round(temperature, 2)
        else:
            if self.grovepi:
                return self.grovepi.temp(pin, sensor_type)
            return 0.0

# Instancia global
gpio = GPIOAdapter()