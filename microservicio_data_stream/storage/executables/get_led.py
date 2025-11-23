import grovepi
try:
    led_pin = 4
    grovepi.pinMode(led_pin, "OUTPUT")
    value = grovepi.digitalRead(led_pin)
except Exception as e:
    print(f"Error: {e}")
    value = 0
