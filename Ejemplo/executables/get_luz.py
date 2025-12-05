import grovepi
try:
    sensor_pin = 2
    grovepi.pinMode(sensor_pin, "INPUT")
    value = grovepi.analogRead(sensor_pin)
except Exception as e:
    print(f"Error: {e}")
    value = 0
