import grovepi
try:
    sensor_pin = 0
    grovepi.pinMode(sensor_pin, "INPUT")
    value = grovepi.temp(sensor_pin, "1.1")
except Exception as e:
    print(f"Error: {e}")
    value = 0
